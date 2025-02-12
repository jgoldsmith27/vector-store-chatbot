const oktaConfig = {
  issuer: "https://dev-72883207.okta.com/oauth2/default",
  clientId: "0oan9lkxwlQn0YzLF5d7",
  redirectUri: window.location.origin + "/login/callback",
  scopes: ["openid", "profile", "email"],
  pkce: true,
  responseType: ["code"],
};

export default oktaConfig;
