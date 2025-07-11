# 🧪 How to Test the Reset Functionality

## 🚀 **Step-by-Step Testing Guide**

### **1. Open the Application**
- Open your web browser
- Go to: **http://localhost:5173**
- You should see the DreamLayer interface

### **2. Navigate to the Right Tab**
- Make sure you're on the **"txt2img"** tab (should be default)
- You should see the generation settings on the left side

### **3. Find the Reset Buttons**
Look for small **"↺ Reset"** buttons in the accordion headers. You should see them in:

**✅ Accordion 1: "Core Generation Settings"**
- This contains the CFG slider we want to test
- Reset button should be visible in the header

**✅ Accordion 2: "Advanced Optional Settings"**
- This contains advanced sliders like face restoration settings
- Reset button should be visible in the header

**❌ Accordion 3: "External Extensions & Add-ons"**
- This should NOT have a reset button (intentionally)

### **4. Test CFG Reset to 10 (Main Test)**

#### **Current State Check:**
1. Open "Core Generation Settings" accordion (should be open by default)
2. Look for the **"CFG Scale"** slider in the "Sampling Settings" section
3. **Note the current value** (probably 7 by default)

#### **Change and Reset Test:**
1. **Change CFG value**: Move the CFG slider to a different value (e.g., 15)
2. **Verify change**: Make sure the slider shows the new value (15)
3. **Click Reset**: Click the **"↺ Reset"** button in the accordion header
4. **Expected Result**: CFG slider should **reset to 10** ✅

### **5. Test Steps Reset to 20**
1. **Change Steps value**: Move the Steps slider to a different value (e.g., 50)
2. **Click Reset**: Click the **"↺ Reset"** button in "Core Generation Settings"
3. **Expected Result**: Steps slider should **reset to 20** ✅

### **6. Test Advanced Settings Reset**
1. **Open accordion**: Click on "Advanced Optional Settings" to expand it
2. **Change values**: Modify some sliders (e.g., set Codeformer Weight to 0.8)
3. **Click Reset**: Click the **"↺ Reset"** button in this accordion header
4. **Expected Results**: All advanced sliders should reset to defaults:
   - Codeformer Weight → 0.5
   - GFPGAN Weight → 0.5
   - Tile Size → 512
   - Tile Overlap → 64

### **7. Test Reset Button Visibility**
1. **Switch tabs**: Try switching to "Custom Workflow" or "LoRA" tabs
2. **Check visibility**: The reset button in accordion 1 should disappear
3. **Switch back**: Return to "Generation" tab
4. **Expected Result**: Reset button should reappear ✅

---

## 🔍 **What to Look For**

### **✅ Success Indicators:**
- Small "↺ Reset" buttons appear in accordion headers
- CFG slider resets to **10** (not 7) when reset button is clicked
- Other sliders reset to their default values
- Reset buttons only appear where they should
- Sliders respond immediately to reset (no page refresh needed)

### **❌ Potential Issues:**
- Reset buttons don't appear → Check browser console for errors
- CFG doesn't reset to 10 → Check if our default value is being used
- Sliders don't update → Check if Slider component is responding to prop changes
- Reset button appears everywhere → Check our conditional logic

---

## 🛠️ **Troubleshooting**

### **If Reset Buttons Don't Appear:**
1. **Check browser console** (F12 → Console tab)
2. **Look for React errors** or TypeScript compilation issues
3. **Refresh the page** to ensure latest code is loaded

### **If CFG Doesn't Reset to 10:**
1. **Check the current value** before resetting
2. **Try changing to a very different value** (e.g., 25) then reset
3. **Verify the reset happens immediately** (no delay)

### **If Nothing Works:**
1. **Check browser console** for JavaScript errors
2. **Verify servers are running**:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:5002
3. **Try refreshing the page** to reload the latest code

---

## 📸 **Expected UI Appearance**

You should see accordion headers that look like this:
```
[1] Core Generation Settings          [↺ Reset] [⌄]
[2] Advanced Optional Settings        [↺ Reset] [⌄]  
[3] External Extensions & Add-ons               [⌄]
```

The reset button should be small, positioned next to the expand/collapse arrow.

---

## ✅ **Success Criteria**
- [ ] Reset buttons appear in correct accordion headers
- [ ] CFG slider resets to **10** (challenge requirement)
- [ ] Steps slider resets to **20**
- [ ] Advanced settings reset to their defaults
- [ ] Reset buttons only appear where appropriate
- [ ] Reset happens immediately when clicked

**Test Status: Ready for manual verification** 🚀