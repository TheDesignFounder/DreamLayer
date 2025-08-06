/**
 * Simple E2E Test Runner for Undo/Redo Functionality
 * 
 * To use this test:
 * 1. Open DreamLayer in your browser
 * 2. Open Developer Tools (F12)
 * 3. Paste this entire script into the Console
 * 4. Run: runUndoRedoTests()
 */

function runUndoRedoTests() {
  console.log('🚀 Starting Undo/Redo E2E Tests');
  
  // Test 1: Basic Prompt Undo/Redo
  async function testBasicPromptUndoRedo() {
    console.log('\n📋 Test 1: Basic Prompt Undo/Redo');
    
    // Find prompt textarea
    const promptTextarea = document.querySelector('textarea[placeholder*="Enter your prompt"]');
    if (!promptTextarea) {
      throw new Error('Prompt textarea not found');
    }
    
    // Type text
    promptTextarea.value = 'A beautiful sunset';
    promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Undo with Ctrl+Z
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'z',
      ctrlKey: true,
      bubbles: true
    }));
    
    // Wait for undo to process
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check if field is blank
    if (promptTextarea.value !== '') {
      throw new Error(`Expected empty field after undo, got: "${promptTextarea.value}"`);
    }
    
    // Redo with Ctrl+Y
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'y',
      ctrlKey: true,
      bubbles: true
    }));
    
    // Wait for redo to process
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check if text is restored
    if (promptTextarea.value !== 'A beautiful sunset') {
      throw new Error(`Expected "A beautiful sunset" after redo, got: "${promptTextarea.value}"`);
    }
    
    console.log('   ✅ Basic Prompt Undo/Redo test passed');
  }
  
  // Test 2: Negative Prompt Undo/Redo
  async function testNegativePromptUndoRedo() {
    console.log('\n📋 Test 2: Negative Prompt Undo/Redo');
    
    // Find negative prompt textarea
    const negativeTextarea = document.querySelector('textarea[placeholder*="Enter negative prompt"]');
    if (!negativeTextarea) {
      throw new Error('Negative prompt textarea not found');
    }
    
    // Clear and type text
    negativeTextarea.value = 'blurry, low quality';
    negativeTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Undo
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'z',
      ctrlKey: true,
      bubbles: true
    }));
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check if field is blank
    if (negativeTextarea.value !== '') {
      throw new Error(`Expected empty field after undo, got: "${negativeTextarea.value}"`);
    }
    
    console.log('   ✅ Negative Prompt Undo/Redo test passed');
  }
  
  // Test 3: Multiple Changes Undo/Redo
  async function testMultipleChangesUndoRedo() {
    console.log('\n📋 Test 3: Multiple Changes Undo/Redo');
    
    const promptTextarea = document.querySelector('textarea[placeholder*="Enter your prompt"]');
    if (!promptTextarea) {
      throw new Error('Prompt textarea not found');
    }
    
    // Clear field first
    promptTextarea.value = '';
    promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Make multiple changes
    const changes = ['Step 1', 'Step 2', 'Step 3'];
    
    for (const change of changes) {
      promptTextarea.value = change;
      promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // Undo twice
    for (let i = 0; i < 2; i++) {
      document.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'z',
        ctrlKey: true,
        bubbles: true
      }));
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // Should be at 'Step 1'
    if (promptTextarea.value !== 'Step 1') {
      throw new Error(`Expected "Step 1" after 2 undos, got: "${promptTextarea.value}"`);
    }
    
    console.log('   ✅ Multiple Changes Undo/Redo test passed');
  }
  
  // Test 4: Undo/Redo Button Click
  async function testUndoRedoButtons() {
    console.log('\n📋 Test 4: Undo/Redo Button Click');
    
    const promptTextarea = document.querySelector('textarea[placeholder*="Enter your prompt"]');
    if (!promptTextarea) {
      throw new Error('Prompt textarea not found');
    }
    
    // Clear and type text
    promptTextarea.value = 'Button test';
    promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Find undo button
    const undoButton = document.querySelector('button[title*="Undo"], button[aria-label*="Undo"]');
    if (!undoButton) {
      console.log('   ⚠️  Undo button not found, skipping button test');
      return;
    }
    
    // Click undo button
    undoButton.click();
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check if field is blank
    if (promptTextarea.value !== '') {
      throw new Error(`Expected empty field after undo button click, got: "${promptTextarea.value}"`);
    }
    
    // Find redo button
    const redoButton = document.querySelector('button[title*="Redo"], button[aria-label*="Redo"]');
    if (!redoButton) {
      console.log('   ⚠️  Redo button not found, skipping redo part');
      return;
    }
    
    // Click redo button
    redoButton.click();
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check if text is restored
    if (promptTextarea.value !== 'Button test') {
      throw new Error(`Expected "Button test" after redo button click, got: "${promptTextarea.value}"`);
    }
    
    console.log('   ✅ Undo/Redo Button Click test passed');
  }
  
  // Test 5: History Counter
  async function testHistoryCounter() {
    console.log('\n📋 Test 5: History Counter');
    
    // Find history counter
    const historyCounter = document.querySelector('[title*="History states"]');
    if (!historyCounter) {
      console.log('   ⚠️  History counter not found, skipping test');
      return;
    }
    
    const initialCount = parseInt(historyCounter.textContent || '1');
    
    // Make a change
    const promptTextarea = document.querySelector('textarea[placeholder*="Enter your prompt"]');
    if (promptTextarea) {
      promptTextarea.value = 'History test';
      promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const newCount = parseInt(historyCounter.textContent || '1');
      if (newCount <= initialCount) {
        throw new Error(`Expected history count to increase from ${initialCount} to ${newCount}`);
      }
    }
    
    console.log('   ✅ History Counter test passed');
  }
  
  // Run all tests
  async function runAllTests() {
    try {
      await testBasicPromptUndoRedo();
      await testNegativePromptUndoRedo();
      await testMultipleChangesUndoRedo();
      await testUndoRedoButtons();
      await testHistoryCounter();
      
      console.log('\n🎉 All tests passed!');
    } catch (error) {
      console.error('\n❌ Test failed:', error.message);
      console.error(error);
    }
  }
  
  runAllTests();
}

// Instructions for use
console.log(`
🧪 Undo/Redo E2E Test Suite Ready!

To run the tests:
1. Navigate to the DreamLayer frontend (txt2img or img2img tab)
2. Run: runUndoRedoTests()

The tests will:
- Type text in prompt fields
- Press Ctrl+Z to undo
- Check if fields are blank
- Press Ctrl+Y to redo
- Verify text is restored
- Test multiple changes
- Test undo/redo buttons (if available)
- Test history counter (if available)
`);

// Make function available globally
window.runUndoRedoTests = runUndoRedoTests;
