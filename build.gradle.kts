plugins {
    java
    id("com.lovelysystems.gradle") version ("1.2.0")
}

lovely {
    gitProject()
    dockerProject("lovelysystems/iris-service")
}

sourceSets["main"].java.setSrcDirs(listOf("src"))

val envDir = project.file("v")
val binDir = envDir.resolve("bin")
val pip = binDir.resolve("pip")
val pipConf = envDir.resolve("pip.conf")
val python = binDir.resolve("python")
val readme = project.file("README.rst")
val req_file = project.file("requirements.txt")
val req_dev_file = project.file("requirements-dev.txt")
val srcDir = projectDir.resolve("src")
val clean = tasks.getByName("clean")
val lovelyEggsDir = buildDir.resolve("lovelyeggs")

val pipConfig = """
[global]
disable-pip-version-check = True
find-links = ${lovelyEggsDir}
"""

val writeVersion by tasks.creating {
    val out = file("VERSION.txt")
    outputs.file(out)
    out.writeText(project.version.toString())
}

val venv by tasks.creating {
    group = "Bootstrap"
    description = "Bootstraps a python virtual environment"
    outputs.files(pip, python, pipConf)
    doLast {
        var res = exec {
            commandLine("python", "-m", "virtualenv", "--version")
            isIgnoreExitValue = true
        }
        if (res.exitValue != 0){
            res = exec {
                commandLine("python", "-m", "pip", "--version")
                isIgnoreExitValue = true
            }
            if (res.exitValue != 0){
                exec {
                    commandLine("python", "-m", "ensurepip")
                }
            }
            exec {
                commandLine("python", "-m", "pip", "--disable-pip-version-check", "install", "virtualenv")
            }
        }
        exec {
            commandLine("python", "-m", "virtualenv", envDir)
        }
        exec {
            commandLine(
                pip, "install", "--upgrade",
                "pip==18.0",
                "setuptools==40.0.0",
                "pip-tools==2.0.2"
            )
        }
        pipConf.writeText(pipConfig)
    }
}
// remove the virtualenv upon clean
clean.doLast { delete(envDir) }

val downloadLovelyEggs by tasks.creating {
    group = "Bootstrap"
    description = "Downloads all eggs from lovely repo"
    dependsOn(venv)
    val req_file = file("requirements-private.txt")
    inputs.files(req_file)
    outputs.dir(lovelyEggsDir)
    doLast {
        exec {
            commandLine(
                binDir.resolve("pip"),
                "download", "--no-deps", "--trusted-host=download.lovelysystems.com",
                "-f", "https://download.lovelysystems.com/eggs/lovely",
                "-f", "https://download.lovelysystems.com/eggs/public",
                "-r", req_file, "--no-binary", ":all", "-d", lovelyEggsDir
            )
        }
    }
}

val downloadSwaggerUI by tasks.creating {
    val swaggerUIFile = buildDir.resolve("downloads/swagger-ui.tar.gz")
    outputs.files(swaggerUIFile)
    doLast {
        // need to check for the file because wgets exit code
        if (!swaggerUIFile.exists()) {
            exec {
                commandLine(
                    "wget", "-nv", "--no-check-certificate", "-O", swaggerUIFile,
                    "https://github.com/swagger-api/swagger-ui/tarball/v2.1.5"
                )
            }
        }
    }
}

val extractSwaggerUI by tasks.creating {
    dependsOn(downloadSwaggerUI)
    val swaggerDir = projectDir.resolve("swagger-ui")
    outputs.files(swaggerDir)
    val tree = tarTree(downloadSwaggerUI.outputs.files.first()).matching {
        include("*/dist/**")
    }
    copy {
        from(tree)
        into(swaggerDir)
    }
}

val swaggerUISymLink by tasks.creating {
    dependsOn(extractSwaggerUI)
    val extractSwaggerDir = extractSwaggerUI.outputs.files.first()
    val swaggerDistDir = extractSwaggerDir.resolve("swagger-api-swagger-ui-b2f82f8/dist")
    doLast {
        exec {
            commandLine(
                "ln", "-s", "-f", swaggerDistDir, srcDir.resolve("iris/service/swaggerui")
            )
        }
    }
}

val nailRequirements by tasks.creating {
    group = "Bootstrap"
    description = "Nails requirements by using pip-compile"
    dependsOn(downloadLovelyEggs)
    val setup_file = file("setup.py")
    inputs.files(setup_file)
    outputs.file(req_file)
    doLast {
        exec {
            commandLine(
                binDir.resolve("pip-compile"),
                setup_file.name,
                "--output-file", req_file.name
            )
        }
    }
}

val nailDevRequirements by tasks.creating {
    group = "Bootstrap"
    description = "Nails requirements of dev dependencies by using pip-compile"
    val dev_req_in = file("requirements-dev.in")
    inputs.files(dev_req_in, nailRequirements.outputs.files)
    // use pserve script as a marker
    outputs.file(req_dev_file)
    doLast {
        exec {
            commandLine(
                binDir.resolve("pip-compile"),
                dev_req_in.name,
                "--output-file", req_dev_file.name
            )
        }
    }
}

val scripts by tasks.creating {
    val testScript = file("bin/test")
    outputs.files(testScript)
    doLast {
        genPythonScript(
            testScript,
            "zope.testrunner:run",
            """
            sys.argv.extend(['--auto-color', '--tests-pattern', '(tests|test_.+)${'$'}',
            '-s', 'iris',
            '--path', os.path.join(base, "src")])
            """.trimIndent()
        )
    }
}

val dev by tasks.creating {
    group = "Bootstrap"
    description = "Installs project development dependencies into the venv"
    dependsOn(venv, writeVersion, scripts)
    inputs.files(nailDevRequirements)
    // use the main executable as a marker
    outputs.files(binDir.resolve("app"))
    doLast {
        exec {
            commandLine(binDir.resolve("pip-sync"), req_dev_file)
        }
        exec {
            commandLine(
                pip, "install", "--no-deps", "-e", projectDir
            )
        }
    }
}

val docs by tasks.creating {
    group = BasePlugin.BUILD_GROUP
    description = "Builds the HTML documentation into build/docs"
    dependsOn("dev")
    inputs.files(fileTree("docs"))
    val out = project.buildDir.resolve("docs")
    outputs.dir(out)
    doLast {
        out.deleteRecursively()
        exec {
            commandLine(binDir.resolve("sphinx-build"), "-E", "docs", out)
        }
    }
}

val sdist by tasks.creating {
    group = BasePlugin.BUILD_GROUP
    description = "Build the source distribution"
    inputs.dir(srcDir)
    inputs.files("setup.py", "MANIFEST.in")
    dependsOn(venv, writeVersion, docs, swaggerUISymLink)
    val out = project.buildDir.resolve("sdist")
    outputs.files(out.resolve("iris.service-${project.version}.tar.gz"))
    doFirst {
        out.deleteRecursively()
    }
    doLast {
        exec {
            commandLine(python, "setup.py", "sdist", "--dist-dir", out)
        }
    }
}

val pytest by tasks.creating {
    dependsOn(dev)
    doLast {
        exec {
            commandLine("bin/test")
        }
    }
}

fun genPythonScript(scriptFile: File, entryPoint: String, initialization: String = "") {
    val (module, function) = entryPoint.split(":", limit = 2)
    val content = """#!${python}
import gevent.monkey
gevent.monkey.patch_all()
import os
base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
base = os.path.dirname(base)
import sys
$initialization
import $module
if __name__ == '__main__':
    sys.exit($module.$function())
"""
    scriptFile.writeText(content)
    scriptFile.setExecutable(true)
}


with(lovely.dockerFiles) {
    from(nailRequirements.outputs)
    from(downloadLovelyEggs) {
        into("lovelyeggs")
    }
    from(pipConf) {
        // remove the private lovely repo, since it is only required for dev dependencies and
        // in the docker build we have no credentials
        filter {
            if (it.contains("find-links")) {
                ""
            } else {
                it
            }
        }
    }
    into("sdist") {
        from(sdist.outputs)
    }
}

tasks.getByName("test").dependsOn(pytest)
