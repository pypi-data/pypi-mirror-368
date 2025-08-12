import { RenderData } from "streamlit-component-lib";
import { lighten } from "color2k";

// Define the Streamlit API directly
function sendMessageToStreamlitClient(type: string, data: any) {
  console.log(type, data);
  const outData = Object.assign(
    {
      isStreamlitMessage: true,
      type: type,
    },
    data
  );
  window.parent.postMessage(outData, "*");
}

const StreamlitAPI = {
  setComponentReady: function () {
    sendMessageToStreamlitClient("streamlit:componentReady", { apiVersion: 1 });
  },
  setFrameHeight: function (height: number) {
    sendMessageToStreamlitClient("streamlit:setFrameHeight", { height });
  },
  setComponentValue: function (value: any) {
    sendMessageToStreamlitClient("streamlit:setComponentValue", { value });
  },
  RENDER_EVENT: "streamlit:render",
  events: {
    addEventListener: function (type: string, callback: (event: CustomEvent) => void) {
      window.addEventListener("message", function (event: MessageEvent) {
        if (event.data.type === type) {
          (event as any).detail = event.data;
          callback(event as unknown as CustomEvent);
        }
      });
    },
  },
};

// Convert hex to rgba for the button border
function hexToRgb(hex: string): string {
  let r = 0, g = 0, b = 0;
  // Remove '#' if present
  hex = hex.replace('#', '');
  // 3-digit hex
  if (hex.length === 3) {
    r = parseInt(hex[0] + hex[0], 16);
    g = parseInt(hex[1] + hex[1], 16);
    b = parseInt(hex[2] + hex[2], 16);
  }
  // 6-digit hex
  else if (hex.length === 6) {
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  }
  return `${r}, ${g}, ${b}`;
}

// Copy button logic
const span = document.body.appendChild(document.createElement("span"));
const textElement = span.appendChild(document.createElement("button"));
const button = span.appendChild(document.createElement("button"));

textElement.className = "st-copy-button";
button.className = "st-copy-button";

let windowRendered = false;

function onRender(event: Event): void {
  if (!windowRendered) {
    const data = (event as CustomEvent<RenderData>).detail;
    const { text, before_copy_label, after_copy_label, show_text } = data.args;

  // Extract theme data from RenderData
  const { theme } = data;
  if (theme) {
    const lightenedBg05 = lighten(theme.backgroundColor, 0.025);

    // Set CSS variables based on Streamlit theme
    document.documentElement.style.setProperty('--primary-color', theme.primaryColor);
    document.documentElement.style.setProperty('--background-color', theme.backgroundColor);
    document.documentElement.style.setProperty('--text-color', theme.textColor);
    // rbg is needed to apply alpha in the CSS
    document.documentElement.style.setProperty('--text-color-rgb', hexToRgb(theme.textColor));
    document.documentElement.style.setProperty('--secondary-background-color', theme.secondaryBackgroundColor);
    // Calculate the button color
    document.documentElement.style.setProperty('--lightened-bg05', lightenedBg05);  
  }

    button.textContent = before_copy_label;

    if (show_text) {
      textElement.textContent = text;
      textElement.style.display = "inline";
    } else {
      textElement.style.display = "none";
    }

    const copyToClipboard = function () {
      navigator.clipboard.writeText(text.trim());
      button.textContent = after_copy_label;
      StreamlitAPI.setComponentValue(true);
      setTimeout(() => {
        if (!button) return;
        button.textContent = before_copy_label;
      }, 1000);
    };

    button.addEventListener("click", copyToClipboard);
    textElement.addEventListener("click", copyToClipboard);

    windowRendered = true;
  }
  StreamlitAPI.setFrameHeight(40);
}

StreamlitAPI.events.addEventListener(StreamlitAPI.RENDER_EVENT, onRender);
StreamlitAPI.setComponentReady();
StreamlitAPI.setFrameHeight(40);
