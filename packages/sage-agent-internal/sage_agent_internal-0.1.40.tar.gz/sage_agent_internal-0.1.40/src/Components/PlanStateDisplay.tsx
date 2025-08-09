import * as React from 'react';
import { Widget } from '@lumino/widgets';
import { ReactWidget } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { marked } from 'marked';

/**
 * Interface for the Plan state
 */
interface IPlanState {
  isVisible: boolean;
  currentStep?: string;
  nextStep?: string;
  source?: string;
  isLoading: boolean;
}

/**
 * React component for displaying Plan state content
 */
interface PlanStateContentProps {
  isVisible: boolean;
  currentStep?: string;
  nextStep?: string;
  source?: string;
  isLoading: boolean;
}

function PlanStateContent({
  isVisible,
  currentStep,
  nextStep,
  source,
  isLoading
}: PlanStateContentProps): JSX.Element | null {
  const [isSourceExpanded, setIsSourceExpanded] = React.useState(false);
  const [renderedSource, setRenderedSource] = React.useState<string>('');

  // Render markdown source content
  React.useEffect(() => {
    if (source && source.trim()) {
      const renderMarkdown = async () => {
        try {
          marked.setOptions({
            gfm: true,
            breaks: false
          });
          const html = await marked.parse(source);
          setRenderedSource(html);
        } catch (error) {
          console.error('Error rendering markdown:', error);
          // Fall back to escaped HTML
          const escaped = source
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
          setRenderedSource(escaped);
        }
      };
      renderMarkdown();
    } else {
      setRenderedSource('');
    }
  }, [source]);

  if (!isVisible) {
    return null;
  }

  const hasSource = source && source.trim();

  return (
    <div className="sage-ai-plan-state-display">
      <div className="sage-ai-plan-state-header">
        {isLoading && <div className="sage-ai-plan-state-loader" />}
        <div className="sage-ai-plan-state-content">
          <div className="sage-ai-plan-current-step">
            <span className="sage-ai-plan-current-text">
              {currentStep || 'No current step'}
            </span>
          </div>

          {(nextStep || hasSource) && (
            <div className="sage-ai-plan-bottom-row">
              {nextStep && (
                <div className="sage-ai-plan-next-text">Next: {nextStep}</div>
              )}
            </div>
          )}
        </div>
        {hasSource && (
          <button
            className="sage-ai-plan-source-toggle"
            onClick={() => setIsSourceExpanded(!isSourceExpanded)}
            aria-expanded={isSourceExpanded}
            type="button"
            title="Toggle source details"
          >
            <svg
              width="17"
              height="18"
              viewBox="0 0 17 18"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M3.54134 6.65503L13.458 6.65503L8.49967 11.3448L3.54134 6.65503Z"
                fill="#949494"
              />
            </svg>
          </button>
        )}
      </div>

      {hasSource && (
        <div
          className={`sage-ai-plan-source-content ${isSourceExpanded ? 'expanded' : 'collapsed'}`}
        >
          <div
            className="sage-ai-plan-source-markdown"
            dangerouslySetInnerHTML={{ __html: renderedSource }}
          />
        </div>
      )}
    </div>
  );
}

/**
 * Component for displaying Plan processing state above the chatbox
 */
export class PlanStateDisplay extends ReactWidget {
  private _state: IPlanState;
  private _stateChanged = new Signal<this, IPlanState>(this);

  constructor() {
    super();
    this._state = {
      isVisible: false,
      currentStep: undefined,
      nextStep: undefined,
      source: undefined,
      isLoading: false
    };
    this.addClass('sage-ai-plan-state-widget');
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, IPlanState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <PlanStateContent
        isVisible={this._state.isVisible}
        currentStep={this._state.currentStep}
        nextStep={this._state.nextStep}
        source={this._state.source}
        isLoading={this._state.isLoading}
      />
    );
  }

  /**
   * Update the plan state with current and next step information
   * @param currentStep The current step text
   * @param nextStep The next step text
   * @param source The source content in markdown format
   */
  public async updatePlan(
    currentStep?: string,
    nextStep?: string,
    source?: string,
    isLoading?: boolean
  ): Promise<void> {
    const shouldShow = !!(currentStep || nextStep);

    this._state = {
      isVisible: shouldShow,
      currentStep,
      nextStep,
      source,
      isLoading: isLoading ?? !!currentStep
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the plan state display
   */
  public show(): void {
    this._state = {
      ...this._state,
      isVisible: true
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Hide the plan state display
   */
  public hide(): void {
    this._state = {
      ...this._state,
      isVisible: false
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Set the loading state
   * @param loading Whether the plan is currently loading
   */
  public setLoading(loading: boolean): void {
    this._state = {
      ...this._state,
      isLoading: loading
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update only the current step text
   * @param currentStep The current step text
   */
  public updateCurrentStep(currentStep: string): void {
    this._state = {
      ...this._state,
      currentStep,
      isVisible: true
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update only the next step text
   * @param nextStep The next step text
   */
  public updateNextStep(nextStep: string): void {
    this._state = {
      ...this._state,
      nextStep
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update only the source content
   * @param source The source content in markdown format
   */
  public updateSource(source: string): void {
    this._state = {
      ...this._state,
      source
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Check if the state display is currently visible
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  /**
   * Get the current state
   */
  public getState(): IPlanState {
    return { ...this._state };
  }

  /**
   * Get the widget for adding to layout (for backwards compatibility)
   */
  public getWidget(): Widget {
    return this;
  }
}
