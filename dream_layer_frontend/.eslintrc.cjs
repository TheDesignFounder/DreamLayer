module.exports = {
    root: true,
    parser: '@typescript-eslint/parser',
    extends: [
        'airbnb',
        'airbnb-typescript',
        'airbnb/hooks',
        'plugin:prettier/recommended',
    ],
    parserOptions: {
        project: './tsconfig.eslint.json',
    },
    settings: {
        react: { version: 'detect' },
        'import/resolver': {
            typescript: {
                project: './tsconfig.eslint.json',
            },
        },
    },
    rules: {
        'react/react-in-jsx-scope': 'off',
        'react/prop-types': 'off',
        'import/prefer-default-export': 'off',
        'react/jsx-props-no-spreading': 'off',
    },
};