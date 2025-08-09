import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
const styleMenus = `
    .p-panel-content-container{
        display: none;
    }
    // .side-tool-bar-container.small-sidebar{
    //     display: none;
    // }
    .comfyui-menu.flex.items-center{
        display: none;
    }
    .p-dialog-mask.p-overlay-mask.p-overlay-mask-enter.p-dialog-bottomright{
        display: none !important;
    }
    body .bizyair-comfy-floating-button{
        display: none;
    }
    .bizy-select-title-container{
        display: none;
    }
    .p-button.p-component.p-button-outlined.p-button-sm{
        display: none;
    }
    .workflow-tabs-container{
        display: none;
    }
    body .comfyui-body-bottom{
        display: none;
    }
    #comfyui-body-bottom{
        display: none;
    }
    .p-button.p-component.p-button-icon-only.p-button-text.model-library-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
    .p-button.p-component.p-button-icon-only.p-button-text.workflows-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
    .p-button.p-component.p-button-icon-only.p-button-text.mtb-inputs-outputs-tab-button.side-bar-button.p-button-secondary{
        display: none;
    }
    body div.side-tool-bar-end{
        display: none;
    }
`
app.registerExtension({
    name: "comfy.BizyAir.Style",
    async setup() {
        $el("style", {
            textContent: styleMenus,
            parent: document.head,
        });
        window.addEventListener('load', () => {
           document.querySelector('[data-pc-section=mask]').style.display = 'none'
        });
    },
});
