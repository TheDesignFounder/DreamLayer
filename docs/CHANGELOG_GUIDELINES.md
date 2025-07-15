# Changelog Contribution Guidelines 🚀

DreamLayer AI uses a **"show‑your‑work"** approach so every new feature is immediately verifiable by reviewers and users.

---

## How to Contribute

### 1. Create Your PR
When you create a Pull Request, the template will automatically appear with evidence requirements.

### 2. Provide Evidence
Simply paste your evidence directly in the PR description:

- **UI Screenshot** - Screenshot of the UI changes
- **Generated Image** - Image created with your changes  
- **Logs** - Logs that verify your changes work
- **Tests** - Test results (optional)

### 3. No File Organization Needed
Just paste evidence inline in the PR description. No need to organize files or assets.

---

## Example PR Description

```markdown
## Description
Fixed duplicate sampling settings in img2img interface.

## Changes Made
- Removed duplicate "2. Sampling Settings" header
- Reordered sections for better UX

## Evidence Required ✅

### UI Screenshot
![Before](https://example.com/before.png)
![After](https://example.com/after.png)

### Generated Image
![Generated with fix](https://example.com/generated.png)

### Logs
```text
2025-07-11 19:16:50 - INFO - Sampling settings working correctly
2025-07-11 19:16:51 - INFO - Image generated successfully
```

### Tests (Optional)
```text
pytest -q
24 passed in 3.2s
```
```

---

## Make it Discoverable

Add to your README.md:

```markdown
## Contributing

- Create a PR and follow the evidence requirements in the template.
```

Happy shipping! ♥
