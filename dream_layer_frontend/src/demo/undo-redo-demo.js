/**
 * Demo Script for Undo/Redo Functionality
 * 
 * This script demonstrates the undo/redo system in action.
 * Run this in the browser console after opening DreamLayer.
 */

function demoUndoRedo() {
  console.log('🎬 Starting Undo/Redo Demo');
  
  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
  
  async function runDemo() {
    // Find the prompt textarea
    const promptTextarea = document.querySelector('textarea[placeholder*="Enter your prompt"]');
    if (!promptTextarea) {
      console.error('❌ Could not find prompt textarea');
      return;
    }
    
    console.log('📝 Starting demo with prompt textarea...');
    
    // Demo sequence
    const demoSteps = [
      { text: 'A beautiful landscape', delay: 300 },
      { text: 'A beautiful landscape with mountains', delay: 300 },
      { text: 'A beautiful landscape with mountains and a lake', delay: 300 },
      { text: 'A beautiful landscape with mountains and a lake at sunset', delay: 300 }
    ];
    
    // Type each step
    for (let i = 0; i < demoSteps.length; i++) {
      const step = demoSteps[i];
      console.log(`🎭 Step ${i + 1}: "${step.text}"`);
      
      promptTextarea.value = step.text;
      promptTextarea.dispatchEvent(new Event('input', { bubbles: true }));
      
      await sleep(step.delay);
    }
    
    console.log('⏪ Starting undo sequence...');
    
    // Undo sequence
    for (let i = 0; i < demoSteps.length; i++) {
      await sleep(800);
      console.log(`⏪ Undo ${i + 1}`);
      
      document.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'z',
        ctrlKey: true,
        bubbles: true
      }));
      
      await sleep(100);
      console.log(`   Current text: "${promptTextarea.value}"`);
    }
    
    console.log('⏩ Starting redo sequence...');
    
    // Redo sequence
    for (let i = 0; i < demoSteps.length; i++) {
      await sleep(800);
      console.log(`⏩ Redo ${i + 1}`);
      
      document.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'y',
        ctrlKey: true,
        bubbles: true
      }));
      
      await sleep(100);
      console.log(`   Current text: "${promptTextarea.value}"`);
    }
    
    console.log('✨ Demo complete!');
    console.log('🎯 Try it yourself:');
    console.log('   - Type in the prompt field');
    console.log('   - Press Ctrl+Z to undo');
    console.log('   - Press Ctrl+Y to redo');
    console.log('   - Use the undo/redo buttons in the UI');
  }
  
  runDemo().catch(console.error);
}

// Make demo available globally
window.demoUndoRedo = demoUndoRedo;

console.log(`
🎬 Undo/Redo Demo Ready!

To run the demo:
1. Make sure you're on the DreamLayer frontend
2. Run: demoUndoRedo()

The demo will:
- Type several prompts automatically
- Undo each change step by step
- Redo each change step by step
- Show the current state at each step
`);
