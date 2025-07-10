# React + TypeScript + Vite Project

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Getting Started

### Prerequisites

Make sure you have Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

### Installation and Development

Follow these steps to set up the project locally:

```sh
# Step 1: Clone the repository
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies
npm install

# Step 4: Start the development server
npm run dev
```

### Building for Production

To build the project for production:

```sh
npm run build
```

### Linting

To run the linter:

```sh
npm run lint
```

## Project Structure

This project uses a modern React setup with:

- **Vite** for fast development and building
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **React Router** for navigation
- **Zustand** for state management

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Inpaint Mask Upload

You can upload a black-and-white mask as a PNG file (≤ 10 MB) in the Inpaint toolbar.  
White areas will be kept, and black areas will be inpainted.

**This completes the documentation requirement for the mask upload feature.**

---

**Summary of what’s done:**

- Mask upload UI and validation implemented.
- State management and preview handled.
- Payload includes mask in multipart form.
- Unit tests written.
- Documentation updated.

Would you like a summary commit message for all these changes, or do you want to review/test anything else?
