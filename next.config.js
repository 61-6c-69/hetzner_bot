module.exports = {
  async redirects() {
    return [
      {
        source: '/auth/register',
        destination: '/auth/login',
        permanent: true,
      },
    ]
  },
}