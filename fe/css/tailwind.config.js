module.exports = {
  darkMode: 'media',
  purge: {
    enabled: process.env.NODE_ENV == "production",
    content: ['../../tfstater/templates/**/*.html'],
  }
}
