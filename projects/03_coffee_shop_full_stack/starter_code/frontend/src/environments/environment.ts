/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:57959', // the running FLASK api server url
  auth0: {
    url: 'acm123', // the auth0 domain prefix
    audience: 'image', // the audience set for the auth0 app
    clientId: '1L9xw5s0XGD5po82oL6LoGJxLOKNYJtP', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:57918', // the base url of the running ionic app. Must put http://localhost:57064/tabs/user-page in auth0 website
  }
};
