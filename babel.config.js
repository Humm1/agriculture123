module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./src'],
          extensions: ['.ios.js', '.android.js', '.js', '.jsx', '.json', '.tsx', '.ts'],
          alias: {
            '@context': './src/context',
            '@services': './src/services',
            '@screens': './src/screens',
            '@components': './src/components',
            '@navigation': './src/navigation',
            '@config': './src/config',
            '@theme': './src/theme',
          },
        },
      ],
    ],
  };
};
