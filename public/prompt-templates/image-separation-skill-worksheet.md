# SKILL PLANNING WORKSHEET

<!--
Instructions (for the Human):
* Fill in any part of this template you like, it's completely OK to leave part of the request empty -
  the agent will fill in the details on your behalf
-->

!!!SPECIAL INSTRUCTIONS (for Agent)
Wherever possible, as you create this new skill, please try to quote the original user verbatim, even if this means copying in their original phrasing, and then suggesting a full explaination that expands on what you percieve to be their intent.

If there are areas you feel uncertain of, or that you are reaching, please voice these with the user and discuss with them. They made be able to provide you with extra information. It's safe to not already know everything; your job is to collaborate with the user so they can give you the guidance that you need to complete the task.

---

# Part 1: Understanding the Skill with Concrete Examples

## 1. Overview

What will this skill do? Describe it in 2–3 sentences.
* Parse composite images into separate images based on spatial connectivity, detecting distinct regions that are not physically connected
* Extract each connected component as an individual image file with descriptive naming based on position or content
* Handle various image formats with configurable thresholds for separation distance and minimum component size

Trigger keywords: separate images, split image, extract components, parse image, divide image

---

## 2. Invocation

### Slash command
`/separate-images <image_path> [--min-area 500] [--padding 10]`

### Conversational triggers
What would a user say that should activate this skill?
"if I give you an image, what would it take to parse it into separate images based on how closely connected the images are to one another"
"can you separate this image into individual images"
"split this composite image"
"extract each component from this image"

### Context triggers
What situation or file type should activate this skill automatically?
* User provides a composite image with multiple distinct visual elements
* User mentions wanting to separate or split images

### Options
- [ ] **Manual only** — require `/slash-command` to invoke
- [x] **Auto-invoke** — Claude activates when context matches (default)

---

## 3. Command Line Arguments

| Argument | Description | Required? |
|----------|-------------|-----------|
| `$0` | Image file path | Yes |
| `$1` | --min-area: Minimum pixel area for valid components (default 500) | No |
| `$2` | --padding: Pixels to add around extracted images (default 10) | No |
| `$3` | --threshold: Brightness threshold for background (default 250) | No |
| `$4` | --output: Output directory path | No |

Or freeform `$ARGUMENTS`: Path to image file with optional parameters

---

## 4. Workflow Shape

### Is this one linear path, or does the skill handle different types of requests?

Describe 1–4 different things a user might ask this skill to do, and how the approach differs for each.

| User wants to... | Workflow |
|-------------------|----------|
| Separate a composite image | → Analyze connectivity → Extract components → Save |
| Analyze image structure first | → Show component stats → Let user adjust parameters |
| Extract with specific names | → Detect components → Apply custom naming → Save |
| Process batch of images | → Loop through files → Apply same parameters → Save all |

### Workflow steps

**Workflow: Basic Separation**
1. Load the image using PIL
2. Convert to grayscale for analysis
3. Apply threshold to create binary image (background vs foreground)
4. Use connected component analysis to find distinct regions
5. Filter components by minimum area
6. Extract each component with padding
7. Sort by vertical position (top to bottom)
8. Save with descriptive filenames
9. Return: List of saved file paths

**Workflow: Analysis First**
1. Load and analyze the image
2. Report number of components found
3. Show size and position of each component
4. Let user decide minimum area threshold
5. Proceed with extraction using chosen parameters
6. Return: Component statistics and saved files

---

## 5. Known Failure Modes

What does Claude reliably get wrong when attempting this task without guidance? Be specific — these should be concrete mistakes, not general advice.

| What Claude does wrong | What it should do instead |
|------------------------|--------------------------|
| Detects text as separate components | Use higher min-area threshold (>20000 for illustrations) |
| Tries to use cv2 without checking installation | Check for PIL first (usually pre-installed), offer cv2 as alternative |
| Uses system pip without --system flag | Use `uv pip install --system` or check existing packages first |
| Creates virtual environment unnecessarily | Use existing Python environment when packages available |
| Includes too much whitespace in extraction | Adjust padding parameter based on image content |

---

## 6. Guidelines

| Always | Never |
|--------|-------|
| Check if PIL/Pillow is already available | Install packages without checking first |
| Analyze connectivity before extraction | Assume default parameters work for all images |
| Sort components by position for consistent ordering | Extract in random order |
| Provide descriptive output showing what was extracted | Silently save files without feedback |

**Ask user if:**
- Minimum area threshold needs adjustment (if too many/few components detected)
- Custom naming scheme is preferred
- Different output directory is needed

---

## 7. Error Handling

### Input errors

| Condition | Response |
|-----------|----------|
| Image file not found | "Error: Image file not found at {path}" |
| Invalid image format | "Error: Could not read image - ensure it's a valid image file" |
| No components found | "No distinct components found - try adjusting threshold or min-area" |

### Output verification

How should Claude verify that what it produced is actually correct before delivering it? What are the most common ways the output can be subtly wrong?

**Content checks:**
- [x] Verify expected number of components extracted
- [x] Check that component sizes are reasonable (not too small/large)
- [x] Ensure no overlapping bounding boxes

**Visual/structural checks:**
- [x] Components are sorted consistently (by position)
- [x] File names match content order
- [x] Output directory was created successfully

**Automated checks** (scripts, linters, validators to run):
- Run with --analyze flag first to preview
- Check saved file sizes are reasonable

Should Claude fix and re-verify in a loop?
[x] Yes / [] No

---

## 8. Quality Standards

What does "excellent" look like for this output, beyond just being correct? Describe the quality bar, aesthetic standard, or professional expectation.
* Clean extraction with minimal unnecessary whitespace
* Consistent padding around all components
* Descriptive filenames that indicate content or position
* Preservation of original image quality and transparency

### Degrees of freedom

How much creative latitude should Claude have?

- [x] **Low** — Follow exact specifications. Consistency is critical. Deviation is a bug.
- [ ] **Medium** — Preferred patterns exist, but some adaptation to context is fine.
- [ ] **High** — Multiple approaches are valid. Claude should use judgment and be creative.

---

# PART 2: Planning the Reusable Skill Contents

## 9. Environmental Adaptation

Does this skill behave differently depending on what tools, integrations, and context are available?

### Data sources / inputs
How should Claude get the data it needs? List in order of preference, with fallbacks.

| If available... | Then... |
|-----------------|---------|
| PIL/Pillow installed | Use PIL-based script (preferred - usually pre-installed) |
| OpenCV installed | Use cv2-based script (more features but slower install) |
| Neither available | Install PIL with `uv pip install --system pillow scipy` |

### Output format
Should the output format adapt to the user's situation?

| Context | Preferred format |
|---------|-----------------|
| Single composite image | Individual PNG files with numbered prefixes |
| Batch processing | Organized in subdirectories per source image |
| User hasn't specified | Default to: separated_images/ directory with descriptive names |

### Integration-dependent behavior
List any integrations that unlock different behavior (e.g., Slack, Google Drive, databases):

- If scipy is available: Use optimized connected component analysis
- If scipy is NOT available: Fall back to pure PIL implementation (slower)

---

## 10. File Structure

### What information does Claude need every time vs. only sometimes?

**Always needed** (goes in SKILL.md — kept under ~500 lines):
- Basic separation workflow
- PIL-based implementation
- Common parameter defaults

**Needed only for specific sub-tasks** (goes in separate reference files):

| Reference file | Loaded when... |
|----------------|----------------|
| advanced-filtering.md | User needs complex filtering rules |
| batch-processing.md | Processing multiple images |
| opencv-implementation.md | OpenCV is preferred/required |

### Scripts to bundle

Which operations should be pre-written scripts that Claude runs, rather than code Claude writes from scratch?

| Script | What it does | Why Claude shouldn't improvise this |
|--------|-------------|-------------------------------------|
| separate_images_pil.py | Main separation using PIL | Complex connected component logic needs testing |
| separate_images_cv2.py | OpenCV alternative | Different API, needs careful implementation |
| analyze_components.py | Preview without extraction | Helps users choose parameters |

### Assets to bundle

Templates, fonts, images, or other files the skill needs at runtime:

| Asset | Purpose |
|-------|---------|
| requirements.txt | Package dependencies |
| example_composite.png | Test image for verification |

### Resulting structure

```
separate-images/
├── SKILL.md
├── references/
│   ├── advanced-filtering.md
│   ├── batch-processing.md
│   └── opencv-implementation.md
├── scripts/
│   ├── separate_images_pil.py
│   ├── separate_images_cv2.py
│   └── analyze_components.py
└── assets/
    ├── requirements.txt
    └── example_composite.png
```

---

# PART 3: The Skill in Action

## 11. Example Interaction

Show a complete example of this skill in action, end-to-end.

**User:** "if I give you an image, what would it take to parse it into separate images based on how closely connected the images are to one another"

**Claude should:**
1. Explain the connected component analysis approach
2. Check for available image processing libraries (PIL/Pillow)
3. Create or use the separation script
4. Analyze the provided image to determine component count
5. Run extraction with appropriate parameters (adjusting min-area if needed)
6. Verify: Check that the expected number of images were created
7. Return: List of saved files with their properties (size, position, area)

---

## Notes from Implementation

### Installation Approach
- **No virtual environment used** - Used system Python with `uv pip install --system`
- **Dependencies:** PIL/Pillow (usually pre-installed), scipy, numpy
- **Alternative:** OpenCV (cv2) works but takes longer to build/install

### Key Learnings
- PIL/Pillow is almost always already available in Python environments
- scipy provides efficient connected component analysis via `ndimage.label`
- Default threshold of 250 works well for white backgrounds
- Text and small elements need filtering with min-area parameter
- Components should be sorted by position for consistent ordering

### Reusability
The script is fully reusable with:
- Configurable parameters via command line arguments
- Analysis mode to preview before extraction
- Works with any image format PIL supports
- No hard-coded paths or specific dependencies