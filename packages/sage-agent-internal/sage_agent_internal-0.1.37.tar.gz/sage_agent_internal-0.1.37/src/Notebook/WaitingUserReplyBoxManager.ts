import { AppStateService } from '../AppState';

export class WaitingUserReplyBoxManager {
  private container: HTMLElement | null = null;
  private waitingReplyBox: HTMLElement | null = null;
  private continueButton: HTMLElement | null = null;
  private onContinueCallback: (() => void) | null = null;

  public initialize(container: HTMLElement): void {
    console.log('[WaitingUserReplyBoxManager] initialize() called');
    if (this.waitingReplyBox) {
      console.log('[WaitingUserReplyBoxManager] Already initialized, returning early');
      return;
    }

    this.container = container;
    console.log('[WaitingUserReplyBoxManager] Container set:', container);

    // Create the waiting reply box
    this.waitingReplyBox = document.createElement('div');
    this.waitingReplyBox.className = 'sage-ai-waiting-reply-container';

    const text = document.createElement('div');
    text.className = 'sage-ai-waiting-reply-text';
    text.textContent = 'Sage will continue working after you reply';

    this.waitingReplyBox.appendChild(text);

    // Create the continue button (initially hidden)
    this.continueButton = document.createElement('button');
    this.continueButton.className = 'sage-ai-continue-button';
    this.continueButton.textContent = 'Continue';
    this.continueButton.style.display = 'none';

    this.continueButton.addEventListener('click', () => {
      console.log('[WaitingUserReplyBoxManager] Continue button clicked');
      if (this.onContinueCallback) {
        console.log('[WaitingUserReplyBoxManager] Calling continue callback');
        this.onContinueCallback();
      } else {
        console.warn('[WaitingUserReplyBoxManager] No continue callback set');
      }
      this.hideContinueButton();
    });

    this.waitingReplyBox.appendChild(this.continueButton);

    this.hide();

    // Add to the container
    this.container.appendChild(this.waitingReplyBox);
    console.log('[WaitingUserReplyBoxManager] Waiting reply box added to container');
    console.log('[WaitingUserReplyBoxManager] Initialization complete');
  }

  public hide(): void {
    if (this.waitingReplyBox) {
      this.waitingReplyBox.style.display = 'none';
    }
  }

  public show(): void {
    console.log('[WaitingUserReplyBoxManager] show() called');
    if (this.waitingReplyBox) {
      console.log('[WaitingUserReplyBoxManager] Setting waiting reply box display to block');
      this.waitingReplyBox.style.display = 'block';

      // Check if we should show the continue button
      this.checkAndShowContinueButton();
    } else {
      console.warn('[WaitingUserReplyBoxManager] waitingReplyBox is null in show()');
    }
  }

  public setContinueCallback(callback: () => void): void {
    console.log('[WaitingUserReplyBoxManager] Setting continue callback');
    this.onContinueCallback = callback;
  }

  private checkAndShowContinueButton(): void {
    console.log('[WaitingUserReplyBoxManager] checkAndShowContinueButton() called');
    
    // Get the current thread from chat history manager
    const chatContainer = AppStateService.getState().chatContainer;
    console.log('[WaitingUserReplyBoxManager] chatContainer:', chatContainer);
    if (!chatContainer) {
      console.warn('[WaitingUserReplyBoxManager] No chatContainer found');
      return;
    }

    const currentThread =
      chatContainer.chatWidget.chatHistoryManager.getCurrentThread();
    console.log('[WaitingUserReplyBoxManager] currentThread:', currentThread);
    if (!currentThread) {
      console.warn('[WaitingUserReplyBoxManager] No currentThread found');
      return;
    }

    console.log('[WaitingUserReplyBoxManager] continueButtonShown status:', currentThread.continueButtonShown);
    
    // Show continue button only if it hasn't been shown in this thread before
    if (!currentThread.continueButtonShown) {
      console.log('[WaitingUserReplyBoxManager] Showing continue button for the first time in this thread');
      this.showContinueButton();

      // Mark that continue button has been shown for this thread
      currentThread.continueButtonShown = true;

      // Update the thread in storage
      chatContainer.chatWidget.chatHistoryManager.updateCurrentThreadMessages(
        currentThread.messages,
        currentThread.contexts
      );
    } else {
      console.log('[WaitingUserReplyBoxManager] Continue button already shown in this thread, not showing again');
    }
  }

  private showContinueButton(): void {
    console.log('[WaitingUserReplyBoxManager] showContinueButton() called');
    if (this.continueButton) {
      console.log('[WaitingUserReplyBoxManager] Setting continue button display to inline-block');
      this.continueButton.style.display = 'inline-block';
    } else {
      console.warn('[WaitingUserReplyBoxManager] continueButton is null in showContinueButton()');
    }
  }

  private hideContinueButton(): void {
    console.log('[WaitingUserReplyBoxManager] hideContinueButton() called');
    if (this.continueButton) {
      console.log('[WaitingUserReplyBoxManager] Setting continue button display to none');
      this.continueButton.style.display = 'none';
    } else {
      console.warn('[WaitingUserReplyBoxManager] continueButton is null in hideContinueButton()');
    }
  }
}
