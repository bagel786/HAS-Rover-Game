# Deployment Instructions: Mars Rover Game

This guide explains how to deploy your Mars Rover game to the web using **GitHub Pages**.

## 1. Local Build (Already Done)
The game has been built for the web using `pygbag`. The deployable files are located in:
`build/web/`

This folder contains:
- `index.html`: The main entry point.
- `main.apk`: The packaged Python code and assets.
- `favicon.png`: The game icon.

## 2. Deploying to GitHub Pages

I have organized the project so you can host it easily while keeping your source code safe.

1.  **Repository Setup** (I have done this locally):
    - I created a `docs/` folder containing the web build.
    - I initialized the git repository and added your remote.

2.  **Push to GitHub**:
    - Run the following command in your terminal to upload everything:
      ```bash
      git push -u origin main
      ```

3.  **Enable GitHub Pages**:
    - Go to your repository settings on GitHub: **Settings** > **Pages**.
    - Under **Branch**, select `main`.
    - Under **Folder**, select `/docs`. (This is the key step!)
    - Click **Save**.

4.  **Play**:
    - Your game will be live at `https://bagel786.github.io/HAS-Rover-Game/` in a few minutes.

## 3. Testing
- Open the GitHub Pages URL.
- The game might take a few seconds to load the Python environment.
- Click the screen to focus and use Arrow Keys or WASD to drive!
