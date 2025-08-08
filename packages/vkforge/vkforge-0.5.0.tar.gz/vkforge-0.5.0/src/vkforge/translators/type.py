from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateCore(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeCore VkForgeCore;

struct VkForgeCore
{{
    VkInstance       instance;
    VkSurfaceKHR     surface;
    VkPhysicalDevice physical_device;
    uint32_t         queue_family_index;
    VkDevice         device;
    VkQueue          queue;
    VkSwapchainKHR   swapchain;
    uint32_t         swapchain_size;
    VkImage*         swapchain_images;
    VkImageView*     swapchain_imgviews;
    VkCommandPool    cmdpool;
}};
"""
    output = content.format()

    return output


def CreateBufferAllocType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeBufferAlloc VkForgeBufferAlloc;

struct VkForgeBufferAlloc
{{
    VkBuffer       buffer;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format()

    return output

def CreateImageAllocType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeImageAlloc VkForgeImageAlloc;

struct VkForgeImageAlloc
{{
    VkImage        image;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format()

    return output

def CreateLayout(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeLayout VkForgeLayout;
"""
    output = content.format()

    return output

def GetMaxPipelines(ctx: VkForgeContext):
    references = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.REFERENCES]
    return max(len(references), 1)

def GetMaxPipelineLayouts(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    return max(len(layouts), 1)

def GetMaxDescriptorSetLayouts(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    max_descriptorset_layout = 0
    for layout in layouts:
        if len(layout) > max_descriptorset_layout:
            max_descriptorset_layout = len(layout)
    return max(max_descriptorset_layout, 1)

def GetMaxDescriptorBindings(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    max_descriptor_binding = 0
    for layout in layouts:
        for set1 in layout:
            if len(set1) > max_descriptor_binding:
                max_descriptor_binding = len(set1)
    return max(max_descriptor_binding, 1)

def CreateMaxes(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_MAX_PIPELINES {max_pipelines_value}
#define VKFORGE_MAX_PIPELINE_LAYOUTS {max_pipeline_layouts_value}
#define VKFORGE_MAX_DESCRIPTORSET_LAYOUTS {max_descriptorset_layouts_value}
#define VKFORGE_MAX_DESCRIPTOR_BINDINGS {max_descriptor_bindings_value}
"""
    output = content.format(
        max_pipelines_value=GetMaxPipelines(ctx),
        max_pipeline_layouts_value=GetMaxPipelineLayouts(ctx),
        max_descriptorset_layouts_value=GetMaxDescriptorSetLayouts(ctx),
        max_descriptor_bindings_value=GetMaxDescriptorBindings(ctx)
    )

    return output

def CreateTexture(ctx: VkForgeContext):
    content = """\
typedef struct VkForgeTexture VkForgeTexture;

struct VkForgeTexture
{{
    VkImage image;                      // The actual GPU image
    VkDeviceMemory memory;              // Memory bound to the VkImage
    VkImageView imageView;              // Optional: for sampling/viewing the image
    VkSampler sampler;                  // Sampler used to read from the texture
    uint32_t width;                     // Texture width in pixels
    uint32_t height;                    // Texture height in pixels
    VkSampleCountFlagBits samples;      // Multisample count (e.g., VK_SAMPLE_COUNT_1_BIT)
    VkFormat format;                    // Image format (e.g., VK_FORMAT_R8G8B8A8_UNORM)
}};
"""
    return content.format()

def CreateRender(ctx: VkForgeContext):
    content = """\
typedef enum VkForgeRenderStatus VkForgeRenderStatus;

enum VkForgeRenderStatus
{{
    VKFORGE_RENDER_READY,
    VKFORGE_RENDER_COPYING,
    VKFORGE_RENDER_ACQING_IMG,
    VKFORGE_RENDER_PENGING_ACQ_IMG,
    VKFORGE_RENDER_DRAWING,
    VKFORGE_RENDER_SUBMITTING,
    VKFORGE_RENDER_PENDING_SUBMIT,
}};

typedef struct VkForgeRender VkForgeRender;
typedef void (*VkForgeRenderCallback)(VkForgeRender render);

struct VkForgeRender
{{
    VkPhysicalDevice      physical_device;
    VkSurfaceKHR          surface;
    VkDevice              device;
    VkQueue               queue;
    VkCommandPool         cmdPool;
    VkExtent2D            extent;
    VkCommandBuffer       copyCmdBuf;
    VkCommandBuffer       drawCmdBuf;
    VkForgeRenderCallback copyCallback;
    VkForgeRenderCallback drawCallback;
    VkSwapchainKHR        swapchain;
    VkImage*              images;
    VkImageView*          imgviews;
    uint32_t              index;
    VkFence               acquireImageFence;
    VkFence               submitQueueFence;
    VkSemaphore           copySemaphore;
    VkSemaphore           drawSemaphore;
    VkForgeRenderStatus   status;
    void*                 userData;
}};
"""
    return content.format()

def GetTypeStrings(ctx: VkForgeContext):
    return [
        CreateMaxes(ctx),
        CreateCore(ctx),
        CreateBufferAllocType(ctx),
        CreateImageAllocType(ctx),
        CreateLayout(ctx),
        CreateTexture(ctx),
        CreateRender(ctx)
        
    ]