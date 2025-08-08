import { LabIcon } from '@jupyterlab/ui-components';
import agentModeIcon from '../../style/icons/chat_input/agent-mode.svg';
import agentModeShinyIcon from '../../style/icons/chat_input/agent-mode-shiny.svg';
import handsOnModeIcon from '../../style/icons/chat_input/hands-on-mode.svg';
import askIcon from '../../style/icons/chat_input/ask-mode.svg';
import openModeSelectorIcon from '../../style/icons/chat_input/open.svg';
import sendIcon from '../../style/icons/chat_input/send.svg';
import stopIcon from '../../style/icons/chat_input/stop.svg';
import reapplyIcon from '../../style/icons/chat_input/reapply.svg';

export const AGENT_MODE_ICON = new LabIcon({
  name: 'sage-agent-internal:agent-mode-icon', // unique name for your icon
  svgstr: agentModeIcon // the imported SVG content as string
});

export const AGENT_MODE_SHINY_ICON = new LabIcon({
  name: 'sage-agent-internal:agent-mode-shiny-icon', // unique name for your icon
  svgstr: agentModeShinyIcon // the imported SVG content as string
});

export const HANDS_ON_MODE_ICON = new LabIcon({
  name: 'sage-agent-internal:hands-on-icon',
  svgstr: handsOnModeIcon
});

export const ASK_ICON = new LabIcon({
  name: 'sage-agent-internal:ask-icon',
  svgstr: askIcon
});

export const OPEN_MODE_SELECTOR_ICON = new LabIcon({
  name: 'sage-agent-internal:open-mode-selector-icon',
  svgstr: openModeSelectorIcon
});

export const SEND_ICON = new LabIcon({
  name: 'sage-agent-internal:send-icon',
  svgstr: sendIcon
});

export const STOP_ICON = new LabIcon({
  name: 'sage-agent-internal:stop-icon',
  svgstr: stopIcon
});

export const REAPPLY_ICON = new LabIcon({
  name: 'sage-agent-internal:reapply-icon',
  svgstr: reapplyIcon
});
