import { app } from "../../scripts/app.js";
import '../BizyAir/bizyair_frontend.js'
import { hideWidget } from './tool.js'
const possibleWidgetNames=[
    "clip_name",
    "clip_name1",
    "clip_name2",
    "ckpt_name",
    "lora_name",
    "control_net_name",
    "ipadapter_file",
    "unet_name",
    "vae_name",
    "model_name",
    "instantid_file",
    "pulid_file",
    "style_model_name",
]

// 根据节点名称匹配模型类型
function getModelTypeFromNodeName(nodeName) {
    if (/bizyair/i.test(nodeName)) {
        return null;
    }

    const regex = /^(\w+).*Loader.*/i;
    const match = nodeName.match(regex);
    if (match) {
        return match[1];
    }
    return null;
}

function createSetWidgetCallback(modelType, selectedBaseModels = []) {
    return function setWidgetCallback() {
        const targetWidget = this.widgets.find(widget => possibleWidgetNames.includes(widget.name));
        if (targetWidget) {
            targetWidget.value = targetWidget.value || "to choose"
            targetWidget.mouse = function(e, pos, canvas) {
                try {
                    if (e.type === "pointerdown" || e.type === "mousedown" || e.type === "click" || e.type === "pointerup") {
                        e.preventDefault();
                        e.stopPropagation();
                        e.widgetClick = true;

                        const currentNode = this.node;

                        if (!currentNode || !currentNode.widgets) {
                            console.warn("Node or widgets not available");
                            return false;
                        }

                        if (typeof bizyAirLib !== 'undefined' && typeof bizyAirLib.showModelSelect === 'function') {
                            bizyAirLib.showModelSelect({
                                modelType: [modelType],
                                selectedBaseModels,
                                onApply: (version, model) => {
                                    if (!currentNode || !currentNode.widgets) return;

                                    const currentLora = currentNode.widgets.find(widget => possibleWidgetNames.includes(widget.name));
                                    const currentModel = currentNode.widgets.find(w => w.name === "model_version_id");

                                    if (model && currentModel && version) {
                                        currentLora.value = model;
                                        currentModel.value = version.id;
                                        currentNode.setDirtyCanvas(true);
                                    }
                                }
                            });
                        } else {
                            console.error("bizyAirLib not available");
                        }
                        return false;
                    }
                } catch (error) {
                    console.error("Error handling mouse event:", error);
                }
            };

            // targetWidget.node = this;
            targetWidget.options = targetWidget.options || {};
            targetWidget.options.values = () => [];
            targetWidget.options.editable = false;
            targetWidget.clickable = true;
            targetWidget.processMouse = true;
        }
    }
}

function setupNodeMouseBehavior(node, modelType) {
    hideWidget(node, "model_version_id");

    // 只设置必要的状态信息，不修改onMouseDown（已在上面的扩展中处理）
    if (!node._bizyairState) {
        node._bizyairState = {
            lastClickTime: 0,
            DEBOUNCE_DELAY: 300,
            modelType: modelType
        };
    }
}

app.registerExtension({
    name: "bizyair.hook.load.model",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {

        localStorage.removeItem('workflow')
        sessionStorage.clear()
        const interval = setInterval(() => {
            if (window.switchLanguage) {
                window.switchLanguage('zh')
                clearInterval(interval)
            }
        }, 100)

        const modelType = getModelTypeFromNodeName(nodeData.name);
        if (modelType) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    let model_version_id = this.widgets.find(w => w.name === "model_version_id");
                    if (!model_version_id) {
                        model_version_id = this.addWidget("hidden", "model_version_id", "", function(e){
                            console.log(e)
                        }, {
                            serialize: true,
                            values: []
                        });
                    }
                    console.log(model_version_id)
                    const result = onNodeCreated?.apply(this, arguments);
                    let selectedBaseModels = [];
                    // if (modelType === 'Checkpoint') {
                    //     selectedBaseModels = ['SDXL', 'Pony', 'SD 3.5', 'Illustrious']
                    // }
                    createSetWidgetCallback(modelType, selectedBaseModels).call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },

    async nodeCreated(node) {
        const modelType = getModelTypeFromNodeName(node?.comfyClass);

        if (modelType) {
            setupNodeMouseBehavior(node, modelType);
        }
    }
})
