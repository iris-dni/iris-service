(function (global) {
  global.iris = global.iris || {};
  global.iris.settings = global.iris.settings || {};
  global.iris.settings.platform = {
    name: 'Iris'
  };
  global.iris.settings.swagger = {
    specUrl: 'http://localhost:29080/swagger.json'
  };
  global.iris.settings.ssoProviders = [
    {
      loginUrl: 'http://aaz.azdev.lovelysystems.com/anmelden',
      name: 'AZ Dev'
    }
  ];
}(window));
