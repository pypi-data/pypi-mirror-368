from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateDebugMsgCallback(ctx: VkForgeContext) -> str:
    content = """\
VKAPI_ATTR VkBool32 VKAPI_CALL VkForge_DebugMsgCallback
(
    VkDebugUtilsMessageSeverityFlagBitsEXT severity,
    VkDebugUtilsMessageTypeFlagsEXT type,
    const VkDebugUtilsMessengerCallbackDataEXT* callback,
    void* user
)
{{
    (void)user;

    const char* typeStr = "";
    if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT)
    {{
        typeStr = "[VALIDATION]";
    }} else if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT)
    {{
        typeStr = "[PERFORMANCE]";
    }} else if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT)
    {{
        typeStr = "[GENERAL]";
    }}

    if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT)
    {{
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "%%s %%s", typeStr, callback->pMessage);
    }} else if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT)
    {{
        SDL_LogWarn(SDL_LOG_CATEGORY_APPLICATION, "%%s %%s", typeStr, callback->pMessage);
    }} else if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT ||
               severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT)
    {{
        SDL_Log("%%s %%s", typeStr, callback->pMessage);
    }}

    return VK_FALSE;
}}
"""
    output = content.format()

    return output


def CreateDebugMsgInfo(ctx: VkForgeContext) -> str:
    if not ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageSeverity:
        messageSeverity = "0"
    else:
        messageSeverity = ""
        for ms in ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageSeverity:
            ms = map_value(MSG_SEVERITY_MAP, ms)
            if len(messageSeverity) > 0:
                messageSeverity += "|" + "\n\t\t" + ms
            else:
                messageSeverity += ms
    
    if not ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageType:
        messageType = "0"
    else:
        messageType = ""
        for mt in ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageType:
            mt = map_value(MSG_TYPE_MAP, mt)
            if len(messageType) > 0:
                messageType += " | " + "\n\t\t" + mt
            else:
                messageType += mt

    content = """\
VkDebugUtilsMessengerCreateInfoEXT VkForge_GetDebugUtilsMessengerCreateInfo()
{{
    VkDebugUtilsMessengerCreateInfoEXT createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT;
    createInfo.messageSeverity = 
        {messageSeverity};
    createInfo.messageType =
        {messageType};
    createInfo.pfnUserCallback = VkForge_DebugMsgCallback;
    return createInfo;
}}
"""
    output = content.format(
        messageSeverity=messageSeverity,
        messageType=messageType,
    )

    return output


def CreateScorePhysicalDevice(ctx: VkForgeContext) -> str:
    content = """\
uint32_t VkForge_ScorePhysicalDeviceLimits(VkPhysicalDeviceLimits limits)
{{
    uint32_t score = 0;
    score += limits.maxImageDimension1D;
    score += limits.maxImageDimension2D;
    score += limits.maxImageDimension3D;
    score += limits.maxImageDimensionCube;
    score += limits.maxImageArrayLayers;
    score += limits.maxTexelBufferElements;
    score += limits.maxUniformBufferRange;
    score += limits.maxStorageBufferRange;
    score += limits.maxPushConstantsSize;
    score += limits.maxMemoryAllocationCount;
    score += limits.maxSamplerAllocationCount;
    score += limits.maxBoundDescriptorSets;
    score += limits.maxPerStageDescriptorSamplers;
    score += limits.maxPerStageDescriptorUniformBuffers;
    score += limits.maxPerStageDescriptorStorageBuffers;
    score += limits.maxPerStageDescriptorSampledImages;
    score += limits.maxPerStageDescriptorStorageImages;
    score += limits.maxPerStageDescriptorInputAttachments;
    score += limits.maxPerStageResources;
    score += limits.maxDescriptorSetSamplers;
    score += limits.maxDescriptorSetUniformBuffers;
    score += limits.maxDescriptorSetUniformBuffersDynamic;
    score += limits.maxDescriptorSetStorageBuffers;
    score += limits.maxDescriptorSetStorageBuffersDynamic;
    score += limits.maxDescriptorSetSampledImages;
    score += limits.maxDescriptorSetStorageImages;
    score += limits.maxDescriptorSetInputAttachments;
    score += limits.maxVertexInputAttributes;
    score += limits.maxVertexInputBindings;
    score += limits.maxVertexInputAttributeOffset;
    score += limits.maxVertexInputBindingStride;
    score += limits.maxVertexOutputComponents;
    score += limits.maxTessellationGenerationLevel;
    score += limits.maxTessellationPatchSize;
    score += limits.maxTessellationControlPerVertexInputComponents;
    score += limits.maxTessellationControlPerVertexOutputComponents;
    score += limits.maxTessellationControlPerPatchOutputComponents;
    score += limits.maxTessellationControlTotalOutputComponents;
    score += limits.maxTessellationEvaluationInputComponents;
    score += limits.maxTessellationEvaluationOutputComponents;
    score += limits.maxGeometryShaderInvocations;
    score += limits.maxGeometryInputComponents;
    score += limits.maxGeometryOutputComponents;
    score += limits.maxGeometryOutputVertices;
    score += limits.maxGeometryTotalOutputComponents;
    score += limits.maxFragmentInputComponents;
    score += limits.maxFragmentOutputAttachments;
    score += limits.maxFragmentDualSrcAttachments;
    score += limits.maxFragmentCombinedOutputResources;
    score += limits.maxComputeSharedMemorySize;
    score += limits.maxComputeWorkGroupInvocations;
    score += limits.maxDrawIndexedIndexValue;
    score += limits.maxDrawIndirectCount;
    score += limits.maxSamplerLodBias;
    score += limits.maxSamplerAnisotropy;
    score += limits.maxViewports;
    score += limits.maxTexelOffset;
    score += limits.maxTexelGatherOffset;
    score += limits.maxInterpolationOffset;
    score += limits.maxFramebufferWidth;
    score += limits.maxFramebufferHeight;
    score += limits.maxFramebufferLayers;
    score += limits.framebufferColorSampleCounts;
    score += limits.framebufferDepthSampleCounts;
    score += limits.framebufferStencilSampleCounts;
    score += limits.framebufferNoAttachmentsSampleCounts;
    score += limits.maxColorAttachments;
    score += limits.sampledImageColorSampleCounts;
    score += limits.sampledImageIntegerSampleCounts;
    score += limits.sampledImageDepthSampleCounts;
    score += limits.sampledImageStencilSampleCounts;
    score += limits.storageImageSampleCounts;
    score += limits.maxSampleMaskWords;
    score += limits.maxClipDistances;
    score += limits.maxCullDistances;
    score += limits.maxCombinedClipAndCullDistances;

    return score;
}}
"""
    output = content.format()

    return output


def CreateFence(ctx: VkForgeContext) -> str:
    content = """\
VkFence VkForge_CreateFence(VkDevice device)
{{
    VkFenceCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    VkFence fence = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateFence(device, &createInfo, 0, &fence);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkFence.");
        exit(1);
    }}

    return fence;
}}
"""
    output = content.format()

    return output


def CreateSemaphore(ctx: VkForgeContext) -> str:
    content = """\
VkSemaphore VkForge_CreateSemaphore(VkDevice device)
{{
    VkSemaphoreCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    VkSemaphore semaphore = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateFence(device, &createInfo, 0, &semaphore);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkSemaphore.");
        exit(1);
    }}

    return semaphore;
}}
"""
    output = content.format()

    return output


def CreateCmdImageBarrier(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CmdImageBarrier
(
    VkCommandBuffer cmdbuf,

    VkImage image,
    VkImageLayout oldLayout,
    VkImageLayout newLayout,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags
)
{{
    VkImageMemoryBarrier barrier = {{0}};
    barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barrier.oldLayout = oldLayout;
    barrier.newLayout = newLayout;
    barrier.image = image;
    barrier.srcAccessMask = srcAccessMask;
    barrier.dstAccessMask = dstAccessMask;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.layerCount = 1;

    vkCmdPipelineBarrier(
        cmdbuf,
        srcStageFlags,
        dstStageFlags,
        0,
        0,0,
        0,0,
        1, &barrier
    );
}}


"""
    output = content.format()

    return output


def CreateCmdBufferBarrier(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CmdBufferBarrier
(
    VkCommandBuffer cmdbuf,

    VkBuffer buffer,
    VkDeviceSize offset,
    VkDeviceSize size,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags
)
{{
    VkBufferMemoryBarrier barrier = {{0}};
    barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barrier.buffer = buffer;
    barrier.offset = offset;
    barrier.size = size;
    barrier.srcAccessMask = srcAccessMask;
    barrier.dstAccessMask = dstAccessMask;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;

    vkCmdPipelineBarrier(
        cmdbuf,
        srcStageFlags,
        dstStageFlags,
        0,
        0,0,
        1, &barrier,
        0,0
    );
}}

"""
    output = content.format()

    return output


def CreateGetSurfaceFormat(ctx: VkForgeContext) -> str:
    content = """\
VkSurfaceFormatKHR VkForge_GetSurfaceFormat
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface,
    VkFormat         req_format
)
{{
    VKFORGE_ENUM(
        formats,
        VkSurfaceFormatKHR,
        vkGetPhysicalDeviceSurfaceFormatsKHR,
        64,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < formats_count; i++)
    {{
        if (req_format == formats_buffer[i].format)
            return formats_buffer[i];
    }}

    return formats_buffer[0];
}}

"""
    output = content.format()

    return output


def CreateGetSurfaceCapabilities(ctx: VkForgeContext) -> str:
    content = """\
VkSurfaceCapabilitiesKHR VkForge_GetSurfaceCapabilities
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface
)
{{
    VkSurfaceCapabilitiesKHR surface_cap = {{0}};
    VkResult result = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physical_device, surface, &surface_cap);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to get physical device surface capabilities");
        exit(1);
    }}

    return surface_cap;
}}

"""
    output = content.format()

    return output

def CreateGetSwapchainSize(ctx:VkForgeContext) -> str:
    content = """\
uint32_t VkForge_GetSwapchainSize
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface,
    uint32_t         req_size
)
{{

    VkSurfaceCapabilitiesKHR surface_cap = VkForge_GetSurfaceCapabilities(physical_device, surface);

    if ( surface_cap.maxImageCount == 0 )
    {{
        return req_size;
    }}

    if (req_size <= surface_cap.maxImageCount)
    {{
        return req_size;
    }}

    return surface_cap.minImageCount;
}}

"""
    output = content.format()

    return output

def CreateGetPresentMode(ctx: VkForgeContext) -> str:
    content = """\
VkPresentModeKHR VkForge_GetPresentMode
(
    VkPhysicalDevice physical_device,
    VkSurfaceKHR     surface,
    VkPresentModeKHR req_mode
)
{{
    VKFORGE_ENUM(
        modes,
        VkPresentModeKHR,
        vkGetPhysicalDeviceSurfacePresentModesKHR,
        4,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < modes_count; i++)
    {{
        if (req_mode == modes_buffer[i]) return req_mode;
    }}

    return modes_buffer[0];
}}

"""
    output = content.format()

    return output


def CreateGetMemoryTypeIndex(ctx: VkForgeContext) -> str:
    content = """\
uint32_t VkForge_GetMemoryTypeIndex
(
    VkPhysicalDevice      physical_device,
    uint32_t              typeFilter,
    VkMemoryPropertyFlags properties
)
{{
    VkPhysicalDeviceMemoryProperties memProperties = {{0}};
    vkGetPhysicalDeviceMemoryProperties(physical_device, &memProperties);

    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++)
    {{
        if ((typeFilter & (1 << i)) &&
            (memProperties.memoryTypes[i].propertyFlags & properties) == properties)
        {{
            return i;
        }}
    }}

    SDL_LogError(0, "Failed to find suitable Vulkan memory type");
    exit(1);
    return 0;
}}

"""
    output = content.format()

    return output

def CreateCreateBufferAlloc(ctx: VkForgeContext) -> str:
    content = """\
VkForgeBufferAlloc VkForge_CreateBufferAlloc
(
    VkPhysicalDevice           physical_device,
    VkDevice                   device,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage,
    VkMemoryPropertyFlags      properties
)
{{
    VkResult result;
    VkMemoryRequirements memRequirements;
    VkForgeBufferAlloc allocation = {{0}};

    allocation.buffer = VkForge_CreateBuffer(device, size, usage, &memRequirements);
    allocation.memory = VkForge_AllocDeviceMemory(physical_device, device, memRequirements, properties);
    allocation.size   = memRequirements.size;
    VkForge_BindBufferMemory(device, allocation.buffer, allocation.memory, 0);

    return allocation;
}}
"""
    return content.format()

def CreateCreateImageAlloc(ctx: VkForgeContext) -> str:
    content = """\
VkForgeImageAlloc VkForge_CreateImageAlloc
(
    VkPhysicalDevice           physical_device,
    VkDevice                   device,
    uint32_t                   width,
    uint32_t                   height,
    VkFormat                   format,
    VkImageUsageFlags          usage,
    VkMemoryPropertyFlags      properties
)
{{
    VkResult result;
    VkMemoryRequirements memRequirements;
    VkForgeImageAlloc allocation = {{0}};

    allocation.image  = VkForge_CreateImage(device, width, height, format, usage, &memRequirements);
    allocation.memory = VkForge_AllocDeviceMemory(physical_device, device, memRequirements, properties);
    allocation.size   = memRequirements.size;
    VkForge_BindBufferMemory(device, allocation.image, allocation.memory, 0);

    return allocation;
}}
"""
    return content.format()

def CreateCreateImageOffset(ctx: VkForgeContext) -> str:
    content = """\
VkImage VkForge_CreateOffsetImage
(
    VkDevice                   device,
    VkDeviceMemory             memory,
    VkDeviceSize               offset,
    uint32_t                   width,
    uint32_t                   height,
    VkFormat                   format,
    VkImageUsageFlags          usage
)
{{
    VkImageCreateInfo imageInfo = {{0}};
    imageInfo.sType         = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    imageInfo.imageType     = VK_IMAGE_TYPE_2D;
    imageInfo.extent.width  = width;
    imageInfo.extent.height = height;
    imageInfo.extent.depth  = 1;
    imageInfo.mipLevels     = 1;
    imageInfo.arrayLayers   = 1;
    imageInfo.format        = format;
    imageInfo.tiling        = VK_IMAGE_TILING_OPTIMAL;
    imageInfo.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    imageInfo.usage         = usage;
    imageInfo.samples       = VK_SAMPLE_COUNT_1_BIT;
    imageInfo.sharingMode   = VK_SHARING_MODE_EXCLUSIVE;

    VkImage image;
    VkResult result = vkCreateImage(device, &imageInfo, 0, &image);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to create offset image");
        exit(1);
    }}

    result = vkBindImageMemory(device, image, memory, offset);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to bind offset image memory");
        exit(1);
    }}

    return image;
}}
"""
    return content.format()

def CreateCreateBufferOffset(ctx: VkForgeContext) -> str:
    content = """\
VkBuffer VkForge_CreateOffsetBuffer
(
    VkDevice                   device,
    VkDeviceMemory             memory,
    VkDeviceSize               offset,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage
)
{{
    VkBufferCreateInfo bufferInfo = {{0}};
    bufferInfo.sType       = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size        = size;
    bufferInfo.usage       = usage;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    VkBuffer buffer;
    VkResult result = vkCreateBuffer(device, &bufferInfo, 0, &buffer);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to create offset buffer");
        exit(1);
    }}

    result = vkBindBufferMemory(device, buffer, memory, offset);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to bind offset buffer memory");
        exit(1);
    }}

    return buffer;
}}
"""
    return content.format()

def CreateStagingBuffer(ctx: VkForgeContext):
    content = """VkForgeBufferAlloc VkForge_CreateStagingBuffer
(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkDeviceSize size
)
{{
    return VkForge_CreateBufferAlloc
    (
        physical_device,
        device,
        size,
        VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
        VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
    );
}}
"""
    return content.format()

def CreateTexture(ctx: VkForgeContext):
    content = """\
VkForgeTexture VkForge_CreateTexture
(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkQueue queue,
    VkCommandBuffer commandBuffer,
    const char* filename
)
{{
    VkFormat format = VK_FORMAT_R8G8B8A8_UNORM;
    VkImageUsageFlags usage = VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT;
    VkSamplerAddressMode addressMode = VK_SAMPLER_ADDRESS_MODE_REPEAT;
    VkFilter filter = VK_FILTER_LINEAR;

    VkForgeTexture texture = {{0}};
    
    SDL_Surface* surface = IMG_Load(filename);
    if (!surface) 
    {{
        SDL_LogError(0, "Failed to load texture image: %%s", filename);
        exit(1);
    }}

    if (SDL_BYTESPERPIXEL(surface->format) != 4) 
    {{
        SDL_Surface* converted = SDL_ConvertSurfaceFormat(surface, SDL_PIXELFORMAT_RGBA8888);
        SDL_DestroySurface(surface);
        if (!converted) 
        {{
            SDL_LogError(0, "Failed to convert surface format: %%s", filename);
            return texture;
        }}
        surface = converted;
    }}

    texture.width = surface->w;
    texture.height = surface->h;
    texture.format = format;
    texture.samples = VK_SAMPLE_COUNT_1_BIT;

    VkDeviceSize imageSize = surface->pitch * surface->h;

    VkForgeBufferAlloc staging = VkForge_CreateStagingBuffer(physical_device, device, imageSize);

    void* data;
    vkMapMemory(device, staging.memory, 0, imageSize, 0, &data);
    SDL_memcpy(data, surface->pixels, imageSize);
    vkUnmapMemory(device, staging.memory);
    SDL_DestroySurface(surface);

    VkForgeImageAlloc imageAlloc = VkForge_CreateImageAlloc
    (
        physical_device,
        device,
        texture.width,
        texture.height,
        texture.format,
        usage,
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
    );

    texture.image = imageAlloc.image;
    texture.memory = imageAlloc.memory;

    VkForge_BeginCommandBuffer(commandBuffer);

    VkForge_CmdImageBarrier
    (
        commandBuffer,
        texture.image,
        VK_IMAGE_LAYOUT_UNDEFINED,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
        0,
        VK_ACCESS_TRANSFER_WRITE_BIT,
        VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
        VK_PIPELINE_STAGE_TRANSFER_BIT
    );

    VkForge_CmdCopyBufferToImage
    (
        commandBuffer, 
        staging.buffer,
        texture.image,
        0, 0,
        texture.width, texture.height,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL
    );

    VkForge_CmdImageBarrier
    (
        commandBuffer,
        texture.image,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
        VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
        VK_ACCESS_TRANSFER_WRITE_BIT,
        VK_ACCESS_SHADER_READ_BIT,
        VK_PIPELINE_STAGE_TRANSFER_BIT,
        VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT
    );

    VkForge_EndCommandBuffer(commandBuffer);

    VkFence fence = VkForge_CreateFence(device);
    VkForge_QueueSubmit(device, commandBuffer, 0, 0, 0, fence);
    vkWaitForFences(device, 1, &fence, VK_TRUE, UINT64_MAX);

    vkDestroyFence(device, fence, 0);
    VkForge_DestroyBufferAlloc(device, staging);

    texture.imageView = VkForge_CreateImageView(device, texture.image, format);
    texture.sampler = VkForge_CreateSampler(device, filter, addressMode);

    return texture;
}}
"""
    return content.format()

def CreateBeginCommandBuffer(ctx: VkForgeContext):
    content = """\
void VkForge_BeginCommandBuffer(VkCommandBuffer cmdBuf)
{{
    VkCommandBufferBeginInfo beginInfo = {{0}};
    beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    beginInfo.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;

    VkResult result = vkBeginCommandBuffer(cmdBuf, &beginInfo);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to Begin command buffer");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateEndCommandBuffer(ctx: VkForgeContext):
    content = """\
void VkForge_EndCommandBuffer(VkCommandBuffer cmdBuf)
{{
    VkResult result = vkEndCommandBuffer(cmdBuf);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to End command buffer");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateCopyBufferToImage(ctx: VkForgeContext):
    content = """\
void VkForge_CmdCopyBufferToImage
(
    VkCommandBuffer cmdBuf,
    VkBuffer buffer,
    VkImage image,
    float x, float y,
    float w, float h,
    VkImageLayout layout
)
{{
    VkBufferImageCopy region = {{0}};
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.mipLevel = 0;
    region.imageSubresource.baseArrayLayer = 0;
    region.imageSubresource.layerCount = 1;
    region.imageOffset = (VkOffset3D){{x, y, 0}};
    region.imageExtent = (VkExtent3D){{w, h, 1}};

    vkCmdCopyBufferToImage(
        cmdBuf,
        buffer,
        image,
        layout,
        1,
        &region
    );
}}
"""
    return content.format()

def CreateQueueSubmit(ctx: VkForgeContext):
    content = """\
void VkForge_QueueSubmit
(
    VkQueue queue,
    VkCommandBuffer cmdBuf,
    VkPipelineStageFlags waitStage,
    VkSemaphore waitSemaphore,
    VkSemaphore signalSemaphore,
    VkFence fence
)
{{
    VkSubmitInfo submitInfo = {{0}};
    submitInfo.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    submitInfo.commandBufferCount = 1;
    submitInfo.pCommandBuffers = &cmdBuf;
    submitInfo.pWaitDstStageMask = waitStage;
    submitInfo.pWaitSemaphores = waitSemaphore ? &waitSemaphore : 0;
    submitInfo.pSignalSemaphores = signalSemaphore ? &signalSemaphore : 0;
    submitInfo.waitSemaphoreCount = waitSemaphore ? 1 : 0;
    submitInfo.signalSemaphoreCount = signalSemaphore ? 1 : 0;

    VkResult result = vkQueueSubmit(queue, 1, &submitInfo, fence);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to Queue Submit");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateImageView(ctx: VkForgeContext):
    content = """\
VkImageView VkForge_CreateImageView
(
    VkDevice device,
    VkImage image,
    VkFormat format
)
{{
    VkImageViewCreateInfo viewInfo = {{0}};
    viewInfo.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
    viewInfo.image = image;
    viewInfo.viewType = VK_IMAGE_VIEW_TYPE_2D;
    viewInfo.format = format;
    viewInfo.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    viewInfo.subresourceRange.baseMipLevel = 0;
    viewInfo.subresourceRange.levelCount = 1;
    viewInfo.subresourceRange.baseArrayLayer = 0;
    viewInfo.subresourceRange.layerCount = 1;

    VkResult result;
    VkImageView imageView = VK_NULL_HANDLE;

    result = vkCreateImageView(device, &viewInfo, 0, &imageView);

    if ( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to create ImageView");
        exit(1);
    }}

    return imageView;
}}
"""
    return content.format()

def CreateSampler(ctx: VkForgeContext):
    content = """\
VkSampler VkForge_CreateSampler
(
    VkDevice device,
    VkFilter filter,
    VkSamplerAddressMode addressMode
)
{{
    // Create sampler
    VkSamplerCreateInfo samplerInfo = {{0}};
    samplerInfo.sType = VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO;
    samplerInfo.magFilter = filter;
    samplerInfo.minFilter = filter;
    samplerInfo.addressModeU = addressMode;
    samplerInfo.addressModeV = addressMode;
    samplerInfo.addressModeW = addressMode;
    samplerInfo.anisotropyEnable = VK_TRUE;
    samplerInfo.maxAnisotropy = 16.0f;
    samplerInfo.borderColor = VK_BORDER_COLOR_INT_OPAQUE_BLACK;
    samplerInfo.unnormalizedCoordinates = VK_FALSE;
    samplerInfo.compareEnable = VK_FALSE;
    samplerInfo.compareOp = VK_COMPARE_OP_ALWAYS;
    samplerInfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
    samplerInfo.mipLodBias = 0.0f;
    samplerInfo.minLod = 0.0f;
    samplerInfo.maxLod = 0.0f;

    VkResult result;
    VkSampler sampler = VK_NULL_HANDLE;

    result = vkCreateSampler(device, &samplerInfo, 0, &sampler);

    if ( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to create Sampler");
        exit(1);
    }}

    return sampler;
}}
"""
    return content.format()

def CreateCreateBuffer(ctx: VkForgeContext):
    content = """\
VkBuffer VkForge_CreateBuffer
(
    VkDevice                   device,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage,

    VkMemoryRequirements      *inMemReqs
)
{{
    VkResult result;
    VkBuffer buffer = VK_NULL_HANDLE;

    VkBufferCreateInfo bufferInfo = {{0}};
    bufferInfo.sType       = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size        = size;
    bufferInfo.usage       = usage;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    VkResult result = vkCreateBuffer(device, &bufferInfo, 0, &buffer);
    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to create buffer");
        exit(1);
    }}

    if( inMemReqs )
    {{
        VkMemoryRequirements memRequirements = {{0}};
        vkGetBufferMemoryRequirements(device, buffer, &memRequirements);
        *inMemReqs = memRequirements;
    }}

    return buffer;
}}
"""
    return content.format()

def CreateCreateImage(ctx: VkForgeContext):
    content = """\
VkImage VkForge_CreateImage
(
    VkDevice               device,
    uint32_t               width,
    uint32_t               height,
    VkFormat               format,
    VkImageUsageFlags      usage,

    VkMemoryRequirements  *inMemReqs
)
{{
    VkImage image = VK_NULL_HANDLE;

    VkImageCreateInfo imageInfo = {{0}};
    imageInfo.sType         = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    imageInfo.imageType     = VK_IMAGE_TYPE_2D;
    imageInfo.extent.width  = width;
    imageInfo.extent.height = height;
    imageInfo.extent.depth  = 1;
    imageInfo.mipLevels     = 1;
    imageInfo.arrayLayers   = 1;
    imageInfo.format        = format;
    imageInfo.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    imageInfo.usage         = usage;
    imageInfo.sharingMode   = VK_SHARING_MODE_EXCLUSIVE;
    imageInfo.samples       = VK_SAMPLE_COUNT_1_BIT;
    imageInfo.flags         = 0;

    VkResult result = vkCreateImage(device, &imageInfo, NULL, &image);
    if (result != VK_SUCCESS)
    {{
        SDL_LogError(0, "Failed to create image");
        exit(1);
    }}

    if( inMemReqs )
    {{
        VkMemoryRequirements memRequirements = {{0}};
        vkGetBufferMemoryRequirements(device, image, &memRequirements);
        *inMemReqs = memRequirements;
    }}

    return image;
}}
"""
    return content.format()

def CreateAllocDeviceMemory(ctx: VkForgeContext):
    content = """\
VkDeviceMemory VkForge_AllocDeviceMemory
(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkMemoryRequirements memRequirements,
    VkMemoryPropertyFlags properties
)
{{
    VkMemoryAllocateInfo allocInfo = {{0}};
    allocInfo.sType               = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    allocInfo.allocationSize      = memRequirements.size;
    allocInfo.memoryTypeIndex     = VkForge_GetMemoryTypeIndex
    (
        physical_device,
        memRequirements.memoryTypeBits,
        properties
    );

    VkDeviceMemory memory = VK_NULL_HANDLE;

    VkResult result = vkAllocateMemory(device, &allocInfo, 0, &memory);
    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Allocate Device Memory");
        exit(1);
    }}

    return memory;
}}
"""
    return content.format()

def CreateBindBufferMemory(ctx: VkForgeContext):
    content = """\
void VkForge_BindBufferMemory(VkDevice device, VkBuffer buffer, VkDeviceMemory memory, VkDeviceSize offset)
{{
    VkResult result = vkBindBufferMemory(device, buffer, memory, offset);

    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Bind Buffer to Memory");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateBindImageMemory(ctx: VkForgeContext):
    content = """\
void VkForge_BindImageMemory(VkDevice device, VkImage image, VkDeviceMemory memory, VkDeviceSize offset)
{{
    VkResult result = vkBindBufferMemory(device, image, memory, offset);

    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Image to Memory");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateDestroyBufferAlloc(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyBufferAlloc(VkDevice device, VkForgeBufferAlloc bufferAlloc)
{{
    vkDestroyBuffer(device, bufferAlloc.buffer, 0);
    vkFreeMemory(device, bufferAlloc.memory, 0);
}}
"""
    return content.format()

def CreateDestroyBufferAlloc(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyBufferAlloc(VkDevice device, VkForgeBufferAlloc bufferAlloc)
{{
    vkDestroyBuffer(device, bufferAlloc.buffer, 0);
    vkFreeMemory(device, bufferAlloc.memory, 0);
}}
"""
    return content.format()

def CreateDestroyImageAlloc(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyImageAlloc(VkDevice device, VkForgeImageAlloc imageAlloc)
{{
    vkDestroyImage(device, imageAlloc.image, 0);
    vkFreeMemory(device, imageAlloc.memory, 0);
}}
"""
    return content.format()

def CreateSetColor(ctx: VkForgeContext):
    content = """\
void VkForge_SetColor(const char* hex, float alpha, float color[4])
{{
    // Skip '#' if present
    if (hex[0] == '#') {{
        hex++;
    }}

    // Must be exactly 6 hex digits
    if (strlen(hex) != 6)
    {{
        SDL_LogError(0, "Invalid hex color: %%s\\n", hex);
        exit(1);
    }}

    // Extract pairs
    char rs[3] = {{ hex[0], hex[1], '\\0' }};
    char gs[3] = {{ hex[2], hex[3], '\\0' }};
    char bs[3] = {{ hex[4], hex[5], '\\0' }};

    // Convert hex to int
    int r = (int)strtol(rs, NULL, 16);
    int g = (int)strtol(gs, NULL, 16);
    int b = (int)strtol(bs, NULL, 16);

    // Normalize to [0, 1]
    color[0] = r / 255.0f;
    color[1] = g / 255.0f;
    color[2] = b / 255.0f;
    color[3] = alpha > 1.0 ? 1 : alpha;
}}
"""
    return content.format()

def CreateBeginRendering(ctx: VkForgeContext):
    content = """\
void VkForge_CmdBeginRendering
(
    VkCommandBuffer cmdbuf,
    VkImageView     imgView,
    const char*     clearColorHex,
    float           x,
    float           y,
    float           w,
    float           h
)
{{
    VkRenderingAttachmentInfo colorAttachment = {{0}};
    colorAttachment.sType                     = VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO;
    colorAttachment.imageView                 = imgView;
    colorAttachment.imageLayout               = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
    colorAttachment.loadOp                    = VK_ATTACHMENT_LOAD_OP_CLEAR;
    colorAttachment.storeOp                   = VK_ATTACHMENT_STORE_OP_STORE;

    VkClearValue clearVal       = {{0}};
    clearVal.depthStencil.depth = 1.0f;
    VkForge_SetColor(clearColorHex, 1.0f, clearVal.color.float32);
    colorAttachment.clearValue = clearVal;

    VkRenderingInfo renderingInfo          = {{0}};
    renderingInfo.sType                    = VK_STRUCTURE_TYPE_RENDERING_INFO;
    renderingInfo.renderArea.offset.x      = x;
    renderingInfo.renderArea.offset.y      = y;
    renderingInfo.renderArea.extent.width  = w;
    renderingInfo.renderArea.extent.height = h;
    renderingInfo.layerCount               = 1;
    renderingInfo.colorAttachmentCount     = 1;
    renderingInfo.pColorAttachments        = &colorAttachment;

    vkCmdBeginRendering(cmdbuf, &renderingInfo);
}}
"""
    return content.format()

def CreateEndRendering(ctx: VkForgeContext):
    content = """\
void VkForge_CmdEndRendering(VkCommandBuffer cmdbuf, VkImage image)
{{
    vkCmdEndRendering(cmdbuf);

    VkForge_CmdImageBarrier
    (
        cmdbuf,
        image,
        VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
        VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
        VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT,
        0,
        VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
        VK_PIPELINE_STAGE_2_BOTTOM_OF_PIPE_BIT
    );
}}
"""
    return content.format()

def CreateQueuePresent(ctx: VkForgeContext):
    content = """\
void VkForge_QueuePresent
(
    VkQueue queue,
    VkSwapchainKHR swapchain,
    uint32_t index,
    VkSemaphore waitSemaphore
)
{{
    VkPresentInfoKHR presentInfo = {{0}};
    presentInfo.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    presentInfo.swapchainCount = 1;
    presentInfo.pSwapchains = &swapchain;
    presentInfo.pImageIndices = &index;
    presentInfo.pWaitSemaphores = &waitSemaphore;
    presentInfo.waitSemaphoreCount = 1;

    VkResult result = vkQueuePresentKHR(queue, &presentInfo);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to Present Queue.");
        exit(1);
    }}
}}
"""
    return content.format()

def GetUtilStrings(ctx: VkForgeContext):
    return [
        CreateDebugMsgInfo(ctx),
        CreateDebugMsgCallback(ctx),
        CreateScorePhysicalDevice(ctx),
        CreateGetMemoryTypeIndex(ctx),
        CreateGetSwapchainSize(ctx),
        CreateGetSurfaceFormat(ctx),
        CreateGetSurfaceCapabilities(ctx),
        CreateGetPresentMode(ctx),        
        CreateCmdBufferBarrier(ctx),
        CreateCmdImageBarrier(ctx),        
        CreateFence(ctx),
        CreateSemaphore(ctx),       
        CreateBeginCommandBuffer(ctx),
        CreateEndCommandBuffer(ctx),
        CreateCopyBufferToImage(ctx),
        CreateQueueSubmit(ctx),
        CreateCreateBuffer(ctx),
        CreateCreateBufferAlloc(ctx),
        CreateCreateBufferOffset(ctx),
        CreateCreateImage(ctx),
        CreateCreateImageAlloc(ctx),
        CreateCreateImageOffset(ctx),
        CreateStagingBuffer(ctx),
        CreateImageView(ctx),
        CreateSampler(ctx),
        CreateTexture(ctx),
        CreateAllocDeviceMemory(ctx),
        CreateBindBufferMemory(ctx),
        CreateBindImageMemory(ctx),
        CreateDestroyBufferAlloc(ctx),
        CreateDestroyImageAlloc(ctx),
        CreateSetColor(ctx),
        CreateBeginRendering(ctx),
        CreateEndRendering(ctx),
        CreateQueuePresent(ctx),

    ]
