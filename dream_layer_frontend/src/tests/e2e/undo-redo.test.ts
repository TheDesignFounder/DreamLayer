/**
 * E2E Test Script for Undo/Redo Functionality
 * This script tests the undo/redo system across prompt edits and slider changes
 */

interface TestScenario {
  name: string;
  description: string;
  actions: TestAction[];
}

interface TestAction {
  type: 'type' | 'click' | 'keyboard' | 'slider' | 'verify' | 'wait';
  selector?: string;
  value?: string | number;
  keys?: string[];
  expected?: any;
  timeout?: number;
}

// Test scenarios
const testScenarios: TestScenario[] = [
  {
    name: "Basic Prompt Undo/Redo",
    description: "Test undo/redo with prompt text changes",
    actions: [
      { type: 'click', selector: 'textarea[placeholder*="Enter your prompt"]' },
      { type: 'type', selector: 'textarea[placeholder*="Enter your prompt"]', value: 'A beautiful sunset' },
      { type: 'wait', timeout: 200 }, // Wait for debounce
      { type: 'keyboard', keys: ['Control', 'z'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: '' },
      { type: 'keyboard', keys: ['Control', 'y'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: 'A beautiful sunset' }
    ]
  },
  {
    name: "Negative Prompt Undo/Redo",
    description: "Test undo/redo with negative prompt changes",
    actions: [
      { type: 'click', selector: 'textarea[placeholder*="Enter negative prompt"]' },
      { type: 'type', selector: 'textarea[placeholder*="Enter negative prompt"]', value: 'blurry, low quality' },
      { type: 'wait', timeout: 200 },
      { type: 'keyboard', keys: ['Control', 'z'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter negative prompt"]', expected: '' },
      { type: 'keyboard', keys: ['Control', 'y'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter negative prompt"]', expected: 'blurry, low quality' }
    ]
  },
  {
    name: "Slider Undo/Redo",
    description: "Test undo/redo with slider changes",
    actions: [
      { type: 'slider', selector: 'input[type="range"]', value: 30 }, // Steps slider
      { type: 'wait', timeout: 200 },
      { type: 'keyboard', keys: ['Control', 'z'] },
      { type: 'verify', selector: 'input[type="range"]', expected: 20 }, // Default value
      { type: 'keyboard', keys: ['Control', 'y'] },
      { type: 'verify', selector: 'input[type="range"]', expected: 30 }
    ]
  },
  {
    name: "Multiple Changes Undo/Redo",
    description: "Test undo/redo with multiple sequential changes",
    actions: [
      { type: 'type', selector: 'textarea[placeholder*="Enter your prompt"]', value: 'Step 1' },
      { type: 'wait', timeout: 200 },
      { type: 'type', selector: 'textarea[placeholder*="Enter your prompt"]', value: 'Step 2' },
      { type: 'wait', timeout: 200 },
      { type: 'type', selector: 'textarea[placeholder*="Enter your prompt"]', value: 'Step 3' },
      { type: 'wait', timeout: 200 },
      { type: 'keyboard', keys: ['Control', 'z'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: 'Step 2' },
      { type: 'keyboard', keys: ['Control', 'z'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: 'Step 1' },
      { type: 'keyboard', keys: ['Control', 'z'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: '' },
      { type: 'keyboard', keys: ['Control', 'y'] },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: 'Step 1' }
    ]
  },
  {
    name: "Undo/Redo Buttons",
    description: "Test undo/redo using UI buttons",
    actions: [
      { type: 'type', selector: 'textarea[placeholder*="Enter your prompt"]', value: 'Button test' },
      { type: 'wait', timeout: 200 },
      { type: 'click', selector: 'button[aria-label*="Undo"]' },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: '' },
      { type: 'click', selector: 'button[aria-label*="Redo"]' },
      { type: 'verify', selector: 'textarea[placeholder*="Enter your prompt"]', expected: 'Button test' }
    ]
  },
  {
    name: "History Size Limit",
    description: "Test that history is limited to 25 states",
    actions: [
      ...Array.from({ length: 30 }, (_, i) => [
        { type: 'type' as const, selector: 'textarea[placeholder*="Enter your prompt"]', value: `Test ${i + 1}` },
        { type: 'wait' as const, timeout: 50 }
      ]).flat(),
      // Try to undo more than 25 times
      ...Array.from({ length: 30 }, () => ({ type: 'keyboard' as const, keys: ['Control', 'z'] })),
      { type: 'verify' as const, selector: 'textarea[placeholder*="Enter your prompt"]', expected: 'Test 6' } // Should stop at 25th state back
    ]
  }
];

class E2ETestRunner {
  private results: { [key: string]: boolean } = {};
  private currentTest: string = '';

  async runTests(): Promise<void> {
    console.log('🚀 Starting E2E Tests for Undo/Redo Functionality');
    
    for (const scenario of testScenarios) {
      this.currentTest = scenario.name;
      console.log(`\n📋 Running: ${scenario.name}`);
      console.log(`   Description: ${scenario.description}`);
      
      try {
        await this.runScenario(scenario);
        this.results[scenario.name] = true;
        console.log(`   ✅ PASSED: ${scenario.name}`);
      } catch (error) {
        this.results[scenario.name] = false;
        console.error(`   ❌ FAILED: ${scenario.name}`, error);
      }
    }
    
    this.printResults();
  }

  private async runScenario(scenario: TestScenario): Promise<void> {
    // Reset state before each test
    await this.resetState();
    
    for (const action of scenario.actions) {
      await this.executeAction(action);
    }
  }

  private async executeAction(action: TestAction): Promise<void> {
    switch (action.type) {
      case 'click':
        await this.clickElement(action.selector!);
        break;
      case 'type':
        await this.typeText(action.selector!, action.value as string);
        break;
      case 'keyboard':
        await this.pressKeys(action.keys!);
        break;
      case 'slider':
        await this.setSliderValue(action.selector!, action.value as number);
        break;
      case 'verify':
        await this.verifyValue(action.selector!, action.expected);
        break;
      case 'wait':
        await this.wait(action.timeout || 100);
        break;
    }
  }

  private async clickElement(selector: string): Promise<void> {
    const element = document.querySelector(selector) as HTMLElement;
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    element.click();
    await this.wait(50); // Small delay after click
  }

  private async typeText(selector: string, text: string): Promise<void> {
    const element = document.querySelector(selector) as HTMLInputElement | HTMLTextAreaElement;
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    
    // Clear existing text
    element.value = '';
    element.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Type new text
    element.value = text;
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  private async pressKeys(keys: string[]): Promise<void> {
    const event = new KeyboardEvent('keydown', {
      key: keys[keys.length - 1],
      ctrlKey: keys.includes('Control'),
      metaKey: keys.includes('Meta'),
      shiftKey: keys.includes('Shift'),
      bubbles: true
    });
    
    document.dispatchEvent(event);
    await this.wait(50);
  }

  private async setSliderValue(selector: string, value: number): Promise<void> {
    const element = document.querySelector(selector) as HTMLInputElement;
    if (!element) {
      throw new Error(`Slider not found: ${selector}`);
    }
    
    element.value = value.toString();
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  private async verifyValue(selector: string, expected: any): Promise<void> {
    const element = document.querySelector(selector) as HTMLInputElement | HTMLTextAreaElement;
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    
    const actual = element.value;
    if (actual !== expected) {
      throw new Error(`Expected "${expected}", but got "${actual}"`);
    }
  }

  private async wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async resetState(): Promise<void> {
    // Clear all form fields
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
      textarea.value = '';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    });
    
    const inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
    inputs.forEach(input => {
      (input as HTMLInputElement).value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
    
    // Reset sliders to default values
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
      const defaultValue = slider.getAttribute('data-default') || '20';
      (slider as HTMLInputElement).value = defaultValue;
      slider.dispatchEvent(new Event('input', { bubbles: true }));
    });
    
    await this.wait(300); // Wait for state to settle
  }

  private printResults(): void {
    console.log('\n📊 Test Results Summary:');
    console.log('========================');
    
    let passed = 0;
    let failed = 0;
    
    for (const [testName, result] of Object.entries(this.results)) {
      const status = result ? '✅ PASSED' : '❌ FAILED';
      console.log(`${status}: ${testName}`);
      if (result) passed++;
      else failed++;
    }
    
    console.log(`\n📈 Total: ${passed + failed} tests`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📊 Success Rate: ${((passed / (passed + failed)) * 100).toFixed(1)}%`);
  }
}

// Export for use in browser console or test environment
if (typeof window !== 'undefined') {
  (window as any).UndoRedoE2ETest = E2ETestRunner;
}

export default E2ETestRunner;

// Usage instructions:
// 1. Open the DreamLayer frontend in your browser
// 2. Open browser developer tools (F12)
// 3. Navigate to the Console tab
// 4. Run the following command:
//    const testRunner = new UndoRedoE2ETest();
//    testRunner.runTests();
