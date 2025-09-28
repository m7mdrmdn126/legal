const { override, addWebpackPlugin } = require('customize-cra');
const webpack = require('webpack');

module.exports = override(
  // Suppress deprecation warnings
  addWebpackPlugin(
    new webpack.DefinePlugin({
      'process.env.GENERATE_SOURCEMAP': 'false'
    })
  ),
  (config) => {
    // Suppress webpack dev server deprecation warnings
    if (config.devServer) {
      config.devServer.client = {
        logging: 'warn',
        overlay: {
          errors: true,
          warnings: false
        }
      };
    }
    return config;
  }
);
