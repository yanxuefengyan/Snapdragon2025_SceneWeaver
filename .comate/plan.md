# Task Plan: Fix File Menu Cancel Issue

## Overview
The goal is to resolve the issue where the file menu cancels unexpectedly when a selection is made, causing the program to crash. The fix involves correcting event handling in the menu system and ensuring proper state synchronization.

## Tasks

### 1. Fix Menu Event Handling
- **File**: `src/ui/native_menu.py`
- **Action**: Modify `handle_event` method
- **Details**: Ensure the method returns `True` when an event is handled to signal the engine to skip further event processing
- **Expected Result**: Menu actions are properly consumed without propagating unintended events

### 2. Update Engine Event Processing
- **File**: `src/core/engine.py`
- **Action**: Modify `handle_events` method
- **Details**: Check if the menu handled the event before processing other events
- **Expected Result**: Engine respects menu event handling and doesn't process redundant events

### 3. Add State Synchronization for FPS Display
- **File**: `src/ui/native_menu.py`
- **Action**: Modify view menu handling
- **Details**: Ensure FPS display toggle maintains correct state between menu and engine
- **Expected Result**: FPS display works consistently without causing menu issues

### 4. Implement Basic Edit Menu Functions
- **File**: `src/core/engine.py`
- **Action**: Add cut, copy, paste functionality
- **Details**: Implement placeholder functions for edit menu items to prevent crashes
- **Expected Result**: Edit menu items work without causing program instability

### 5. Test Fixes
- **Action**: Run main program and test file menu functionality
- **Details**: Verify that file menu selections don't cancel unexpectedly and the program doesn't crash
- **Expected Result**: File menu works correctly with no crashes

## Verification
After completing all tasks, run the main program and test the following:
1. Open file menu and select any option
2. Verify the menu doesn't cancel unexpectedly
3. Check that the program remains stable
4. Confirm FPS display toggle works correctly
5. Test edit menu functions (cut/copy/paste)