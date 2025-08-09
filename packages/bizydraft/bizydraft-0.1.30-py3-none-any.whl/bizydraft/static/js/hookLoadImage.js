import { app } from "../../scripts/app.js";
import { fileToOss } from "./uploadFile.js";
import { getCookie, hideWidget } from './tool.js';

app.registerExtension({
    name: "bizyair.image.to.oss",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === 'LoadImage') {
            let workflowParams = null
            document.addEventListener('workflowLoaded', (event) => {
                workflowParams = event.detail;
            });
            nodeType.prototype.onNodeCreated = async function() {
                const image_widget = this.widgets.find(w => w.name === 'image');
                console.log(image_widget)
                // const apiHost = 'http://localhost:3000/api'
                const apiHost = 'https://bizyair.cn/api'
                const node = this;
                let image_list = []
                const getData = async () => {
                    const res = await fetch(`${apiHost}/special/community/commit_input_resource?${
                        new URLSearchParams({
                            url: '',
                            ext: '',
                            current: 1,
                            page_size: 100

                        }).toString()
                    }`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getCookie('bizy_token')}`
                        }
                    })
                    const {data} = await res.json()
                    const list = (data && data.data && data.data.data && data.data.data.list) || []
                    image_list = list.filter(item => item.name).map(item => {
                        return {
                            url: item.url,
                            name: item.name
                        }
                        // return item.url
                    })
                    const image_widget = this.widgets.find(w => w.name === 'image');


                    let image_path_widget = this.widgets.find(w => w.name === 'image_path');
                    if (!image_path_widget) {
                        image_path_widget = this.addWidget("text", "image_path", "", function(){}, {
                            serialize: true
                        });
                        image_path_widget.type = "hidden";
                        // image_path_widget.style = "hidden";
                        image_path_widget.computeSize = () => [0, 0]; // 隐藏显示
                    }
                    hideWidget(this, 'image_path')

                    image_widget.options.values = image_list.map(item => item.name);
                    // console.log(image_widget.value)
                    // image_widget.value = image_list[0].url;
                    // image_widget.value = image_list[0];
                    if (image_list[0] && image_list[0].url) {
                        image_widget.value = image_list[0].name
                        const defaultImageUrl = decodeURIComponent(image_list[0].url);
                        image_path_widget.value = defaultImageUrl;

                        previewImage(node, defaultImageUrl)
                    }
                    image_widget.callback = function(e) {
                        const image_url = decodeURIComponent(image_list.find(item => item.name === e).url);
                        image_path_widget.value = image_url;
                        previewImage(node, image_url)
                    }
                    return true
                }

                await getData()



                if (workflowParams && workflowParams.json.nodes) {
                    const imageNode = workflowParams.json.nodes.find(item => item.type === 'LoadImage')
                    if (imageNode && imageNode.widgets_values && imageNode.widgets_values[2]) {
                        const temp = {
                            name: imageNode.widgets_values[0],
                            url: imageNode.widgets_values[2]
                        }
                        image_list.push(temp)
                        image_widget.value = temp.name
                        image_widget.options.values = image_list.map(item => item.name)
                        previewImage(node, temp.url)

                        requestAnimationFrame(() => {
                            previewImage(node, temp.url)
                        })
                    }
                }
                const upload_widget = this.widgets.find(w => w.name === 'upload');
                upload_widget.callback = async function() {
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = 'image/*';
                    input.onchange = async (e) => {
                        const file = e.target.files[0];
                        await fileToOss(file);

                        getData()
                    }
                    input.click();
                }
            }
        }
    }
})

function previewImage(node, image_url) {
    const img = new Image();
    img.onload = function() {
        node.imgs = [img];
        if (node.graph && node.graph.setDirtyCanvas) {
            node.graph.setDirtyCanvas(true);
        } else {
            console.warn('[BizyAir] 无法访问graph对象进行重绘');
        }

        console.log('[BizyAir] 图片预览加载成功');
    };
    img.onerror = function(err) {
        console.error('[BizyAir] 图片加载失败:', image_url, err);
    };
    img.src = image_url;
}
