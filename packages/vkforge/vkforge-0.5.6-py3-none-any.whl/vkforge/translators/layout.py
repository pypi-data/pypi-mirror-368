from vkforge.context import VkForgeContext
from vkforge.mappings import *

def BuildStageArray(stages, index):
    """Generate a static stage array with a unique name based on index"""
    stage_str = "static uint32_t STAGE_{0}[] = {{ ".format(index)
    for i, stage in enumerate(stages):
        stage_str += f"{stage}"
        if i < len(stages) - 1:
            stage_str += ", "
    stage_str += " };"
    return stage_str

def BuildBind(bindTuple: tuple, index: int, indent=0):
    """Build a bind structure with proper static stage array"""
    bind = "\n"
    bind += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    
    if bindTuple:
        type1, count, stages = bindTuple
        stages = list(stages)

        type1 = map_value(DESCRIPTOR_TYPE_MAP, type1)
        for i in range(len(stages)):
            stages[i] = map_value(SHADER_STAGE_MAP, stages[i])

        bind += "\t" * child_indent + f"{type1},\n"
        bind += "\t" * child_indent + f"{count},\n"
        bind += "\t" * child_indent + f"{len(stages)},\n"
        bind += "\t" * child_indent + f"STAGE_{index}\n"  # Reference static array
    else:
        bind += "\t" * child_indent + "0, 0, 0, NULL\n"
    
    bind += "\t" * indent + "}"  # close bracket
    return bind

def BuildSet1(setList: list, set_index: int, indent=0):
    """Build a descriptor set layout with unique binding names"""
    set1 = "\n"
    set1 += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    
    if setList:
        set1 += "\t" * child_indent + "/** Bindings **/\n"
        set1 += "\t" * child_indent + f"{len(setList)},\n"
        set1 += "\t" * child_indent + "{"  # child open
        child_indent2 = child_indent + 1
        
        # Generate all stage arrays first
        stage_arrays = []
        bind_structures = []
        for i, bind in enumerate(setList):
            if bind:  # Only generate for non-empty bindings
                _, _, stages = bind
                stage_arrays.append(BuildStageArray(stages, f"{set_index}_{i}"))
                bind_structures.append(BuildBind(bind, f"{set_index}_{i}", child_indent2))
        
        # Add stage arrays to the output
        if stage_arrays:
            set1 = "\n".join(stage_arrays) + "\n" + set1
        
        # Add bind structures
        for bind_struct in bind_structures:
            set1 += bind_struct + ",\n"
            
        set1 += "\t" * child_indent + "}\n"  # child close
    else:
        set1 += "\n"
        set1 += "\t" * child_indent + "{0}\n"
    
    set1 += "\t" * indent + "}"  # close bracket
    return set1

def BuildPipelineLayout(layoutList: list, layout_index: int, indent=0):
    """Build a pipeline layout with unique set names"""
    layout = "\n"
    layout += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    
    if layoutList:
        layout += "\t" * child_indent + "/** DescriptorSet Layouts **/\n"
        layout += "\t" * child_indent + f"{len(layoutList)},\n"
        layout += "\t" * child_indent + "{"  # child open
        child_indent2 = child_indent + 1
        
        for i, set1 in enumerate(layoutList):
            layout += BuildSet1(set1, f"{layout_index}_{i}", child_indent2) + ",\n"
            
        layout += "\t" * child_indent + "}\n"  # child close
    else:
        layout += "\n"
        layout += "\t" * child_indent + "{0}\n"
    
    layout += "\t" * indent + "}"  # close bracket
    return layout

def BuildReference(key: str, val: int, indent=0):
    """Build a reference structure"""
    reference = "\n"
    reference += "\t" * indent + "{ "  # open bracket
    reference += f'{val}, "{key}"'
    reference += " }"  # close bracket
    return reference

def BuildReferencedLayoutDesign(layoutsList: list, references: dict, indent=0):
    """Build the complete referenced layout design with all static arrays"""
    layouts = "\n"
    layouts += "\t" * indent + "{\n"  # open bracket
    child_indent = indent + 1
    child_indent2 = child_indent + 1
    
    if layoutsList:
        layouts += "\t" * child_indent + "/** Pipeline Layouts **/\n"
        layouts += "\t" * child_indent + f"{len(layoutsList)},\n"
        layouts += "\t" * child_indent + "{"  # child open
        
        # First collect all stage arrays to put at the beginning
        all_stage_arrays = []
        layout_structures = []
        for i, pipeline_layout in enumerate(layoutsList):
            # We'll let BuildPipelineLayout handle the stage arrays
            layout_structures.append(BuildPipelineLayout(pipeline_layout, i, child_indent2) + ",\n")
        
        # Add layout structures
        for layout_struct in layout_structures:
            layouts += layout_struct
            
        layouts += "\t" * child_indent + "},\n"  # child close

        layouts += "\t" * child_indent + "/** References **/\n"
        layouts += "\t" * child_indent + f"{len(references)},\n"
        layouts += "\t" * child_indent + "{"  # child open
        
        for key, val in references.items():
            layouts += BuildReference(key, val, child_indent2) + ","
            
        layouts += "\n" + "\t" * child_indent + "}\n"  # child close
    else:
        layouts += "\n"
        layouts += "\t" * child_indent + "0, {0}, 0, {0}\n"
    
    layouts += "\t" * indent + "}"  # close bracket
    return layouts

def CreateForgeReferencedLayoutDesign(ctx: VkForgeContext) -> str:
    """Create the complete referenced layout design with all global variables"""
    content = """\
typedef struct VkForgeLayoutBindDesign VkForgeLayoutBindDesign;
struct VkForgeLayoutBindDesign
{{
    uint32_t  type;
    uint32_t  count;
    uint32_t  mode_count;
    uint32_t* mode_buffer;
}};

typedef struct VkForgeLayoutDescriptorSetLayoutDesign VkForgeLayoutDescriptorSetLayoutDesign;
struct VkForgeLayoutDescriptorSetLayoutDesign
{{
    uint32_t bind_design_count;
    VkForgeLayoutBindDesign** bind_design_buffer;
}};
    
typedef struct VkForgeLayoutPipelineLayoutDesign VkForgeLayoutPipelineLayoutDesign;
struct VkForgeLayoutPipelineLayoutDesign
{{
    uint32_t descriptorset_layout_design_count;
    VkForgeLayoutDescriptorSetLayoutDesign** descriptorset_layout_design_buffer;
}};

typedef struct VkForgeLayoutReferenceDesign VkForgeLayoutReferenceDesign;
struct VkForgeLayoutReferenceDesign
{{
    uint32_t    pipeline_layout_design_index; 
    const char* pipeline_name;
}};

typedef struct VkForgeReferencedLayoutDesign VkForgeReferencedLayoutDesign;
struct VkForgeReferencedLayoutDesign
{{
    uint32_t pipeline_layout_design_count;
    VkForgeLayoutPipelineLayoutDesign** pipeline_layout_design_buffer;
    uint32_t reference_count;
    VkForgeLayoutReferenceDesign** reference_buffer;
}};

{static_arrays}

{static_bind_designs}

{static_descriptor_set_layouts}

{static_pipeline_layouts}

{static_references}

static VkForgeReferencedLayoutDesign VKFORGE_REFERENCED_LAYOUT_DESIGN = 
{{
    {pipeline_layout_design_count},
    {pipeline_layout_design_buffer},
    {reference_count},
    {reference_buffer}
}};
"""
    if ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]:
        layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
        references = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.REFERENCES]
        
        # Generate all the static components
        static_components = GetStaticSubComponents(layouts, references)
        
        output = content.format(
            static_arrays=static_components['static_arrays'],
            static_bind_designs=static_components['static_bind_designs'],
            static_descriptor_set_layouts=static_components['static_descriptor_set_layouts'],
            static_pipeline_layouts=static_components['static_pipeline_layouts'],
            static_references=static_components['static_references'],
            pipeline_layout_design_count=len(layouts),
            pipeline_layout_design_buffer="PIPELINE_LAYOUT_DESIGNS",
            reference_count=len(references),
            reference_buffer="REFERENCES"
        )
    else:
        output = content.format(
            static_arrays="",
            static_bind_designs="",
            static_descriptor_set_layouts="",
            static_pipeline_layouts="",
            static_references="",
            pipeline_layout_design_count=0,
            pipeline_layout_design_buffer="NULL",
            reference_count=0,
            reference_buffer="NULL"
        )
    
    return output

def GetStaticSubComponents(layouts, references):
    """Generate all static components needed for the global variable"""
    components = {
        'static_arrays': "",
        'static_bind_designs': "",
        'static_descriptor_set_layouts': "",
        'static_pipeline_layouts': "",
        'static_references': ""
    }
    
    # Generate stage arrays
    stage_arrays = []
    stage_index = 0
    for layout_idx, layout in enumerate(layouts):
        if layout:
            for set_idx, set1 in enumerate(layout):
                if set1:
                    for bind_idx, bind in enumerate(set1):
                        if bind:  # Only for non-empty bindings
                            _, _, stages = bind
                            stages = [map_value(SHADER_STAGE_MAP, stage) for stage in stages]
                            stage_arrays.append(f"static uint32_t STAGE_{layout_idx}_{set_idx}_{bind_idx}[] = {{ {', '.join(map(str, stages))} }};")
                            stage_index += 1
        else:
            stage_arrays.append("/** NO STAGES **/")

    components['static_arrays'] = "\n".join(stage_arrays)
    
    # Generate bind designs
    bind_designs = []
    bind_design_arrays = []
    for layout_idx, layout in enumerate(layouts):
        if layout:
            for set_idx, set1 in enumerate(layout):
                set_bind_designs = []
                if set1:
                    for bind_idx, bind in enumerate(set1):
                        if bind:
                            type1, count, _ = bind
                            type1 = map_value(DESCRIPTOR_TYPE_MAP, type1)
                            bind_designs.append(
                                f"static VkForgeLayoutBindDesign BIND_{layout_idx}_{set_idx}_{bind_idx} = {{\n"
                                f"    {type1}, {count}, {len(stages)}, STAGE_{layout_idx}_{set_idx}_{bind_idx}\n"
                                "};"
                            )
                            set_bind_designs.append(f"&BIND_{layout_idx}_{set_idx}_{bind_idx}")
                        else:
                            set_bind_designs.append("NULL")
                    
                    # Create array for this set's bind designs
                    bind_design_arrays.append(
                        f"static VkForgeLayoutBindDesign* BIND_DESIGNS_{layout_idx}_{set_idx}[] = {{\n"
                        f"    {', '.join(set_bind_designs)}\n"
                        "};"
                    )
        else:
            bind_design_arrays.append("/** NO BINDING **/")
    
    components['static_bind_designs'] = "\n".join(bind_designs + bind_design_arrays)
    
    # Generate descriptor set layouts
    descriptor_set_layouts = []
    descriptor_set_layout_arrays = []
    for layout_idx, layout in enumerate(layouts):
        layout_descriptor_sets = []
        if layout:
            for set_idx, set1 in enumerate(layout):
                if set1:
                    descriptor_set_layouts.append(
                        f"static VkForgeLayoutDescriptorSetLayoutDesign DESCRIPTOR_SET_LAYOUT_{layout_idx}_{set_idx} = {{\n"
                        f"    {len(set1)}, BIND_DESIGNS_{layout_idx}_{set_idx}\n"
                        "};"
                    )
                    layout_descriptor_sets.append(f"&DESCRIPTOR_SET_LAYOUT_{layout_idx}_{set_idx}")
            
            # Create array for this layout's descriptor sets
            descriptor_set_layout_arrays.append(
                f"static VkForgeLayoutDescriptorSetLayoutDesign* DESCRIPTOR_SET_LAYOUTS_{layout_idx}[] = {{\n"
                f"    {', '.join(layout_descriptor_sets) if layout_descriptor_sets else "0, NULL"}\n"
                "};"
            )
        else:
            descriptor_set_layout_arrays.append("/** NO DESCRIPTORSET LAYOUTS **/")
    
    components['static_descriptor_set_layouts'] = "\n".join(descriptor_set_layouts + descriptor_set_layout_arrays)
    
    # Generate pipeline layouts
    pipeline_layouts = []
    for layout_idx, layout in enumerate(layouts):
        layout_str = ""
        layout_str += f"static VkForgeLayoutPipelineLayoutDesign PIPELINE_LAYOUT_{layout_idx} = {{\n"
        if layout:
            layout_str += f"    {len(layout)}, DESCRIPTOR_SET_LAYOUTS_{layout_idx}\n"
        else:
            layout_str += f"    0, NULL\n"
        layout_str +=  "};"
        pipeline_layouts.append(
            layout_str
        )
    
    # Create array of all pipeline layouts
    pipeline_layout_array = (
        "static VkForgeLayoutPipelineLayoutDesign* PIPELINE_LAYOUT_DESIGNS[] = {\n"
        "    " + ",\n    ".join([f"&PIPELINE_LAYOUT_{i}" for i in range(len(layouts))]) + "\n"
        "};"
    )
    
    components['static_pipeline_layouts'] = "\n".join(pipeline_layouts) + "\n" + pipeline_layout_array
    
    # Generate references
    references_list = []
    for i, (key, val) in enumerate(references.items()):
        references_list.append(
            f"static VkForgeLayoutReferenceDesign REFERENCE_{i} = {{\n"
            f"    {val}, \"{key}\"\n"
            "};"
        )
    
    # Create array of references
    references_array = (
        "static VkForgeLayoutReferenceDesign* REFERENCES[] = {\n"
        "    " + ",\n    ".join([f"&REFERENCE_{i}" for i in range(len(references))]) + "\n"
        "};"
    )
    
    components['static_references'] = "\n".join(references_list) + "\n" + references_array
    
    return components

def CreateForgeLayout(ctx: VkForgeContext) -> str:
    """Create the layout structure definition"""
    content = """\
struct VkForgeLayout
{{
    VkSurfaceKHR          surface;
    VkPhysicalDevice      physical_device;
    VkDevice              device;
    uint8_t               pipeline_count;
    VkPipeline            pipeline_buffer[VKFORGE_MAX_PIPELINES];
    uint8_t               pipeline_layout_count;
    VkPipelineLayout      pipeline_layout_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS];
    uint8_t               descriptorset_layout_count[VKFORGE_MAX_PIPELINE_LAYOUTS];
    VkDescriptorSetLayout descriptorset_layout_buffer[VKFORGE_MAX_PIPELINE_LAYOUTS][VKFORGE_MAX_DESCRIPTORSET_LAYOUTS];
}};
"""
    output = content.format()
    return output

def CreatePipelineFunctionStruct(ctx: VkForgeContext) -> str:
    """Generate the PipelineFunction struct and array for all pipelines"""
    content = """\
typedef struct VkForgePipelineFunction VkForgePipelineFunction;
struct VkForgePipelineFunction
{{
    VkPipeline (*CreatePipelineForFunc)(
        VkAllocationCallbacks* allocator,
        void* next,
        VkDevice device,
        VkPipelineLayout pipeline_layout
    );
    const char* pipeline_name;
    uint32_t pipeline_index;
}};

{static_pipeline_functions}

static VkForgePipelineFunction** VKFORGE_PIPELINE_FUNCTIONS = PIPELINE_FUNCTIONS;
static uint32_t VKFORGE_PIPELINE_FUNCTION_COUNT = {pipeline_count};
"""
    if ctx.forgeModel.Pipeline:
        # Generate static pipeline function structs
        pipeline_funcs = []
        for i, pipeline in enumerate(ctx.forgeModel.Pipeline):
            pipeline_funcs.append(
                f"static VkForgePipelineFunction PIPELINE_FUNC_{i} = {{\n"
                f"    VkForge_CreatePipelineFor{pipeline.name},\n"
                f"    \"{pipeline.name}\",\n"
                f"    {i}\n"
                "};"
            )
        
        # Generate the array of pipeline functions
        pipeline_array = (
            "static VkForgePipelineFunction* PIPELINE_FUNCTIONS[] = {\n"
            "    " + ",\n    ".join([f"&PIPELINE_FUNC_{i}" for i in range(len(ctx.forgeModel.Pipeline))]) + "\n"
            "};"
        )
        
        output = content.format(
            static_pipeline_functions="\n".join(pipeline_funcs) + "\n" + pipeline_array,
            pipeline_count=len(ctx.forgeModel.Pipeline)
        )
    else:
        output = content.format(
            static_pipeline_functions="static VkForgePipelineFunction* PIPELINE_FUNCTIONS[] = {NULL};",
            pipeline_count=0
        )
    
    return output

def CreateCreateForgeLayout(ctx: VkForgeContext) -> str:
    content = """\
VkForgeLayout* VkForge_CreateLayout(VkSurfaceKHR surface, VkPhysicalDevice physical_device, VkDevice device)
{{
    assert(device);

    VkForgeLayout* layout = (VkForgeLayout*)SDL_malloc(sizeof(VkForgeLayout));
    if (!layout)
    {{
        SDL_LogError(0, "Failed to allocate memory for VkForgeLayout");
        exit(1);
    }}

    // Initialize all counts to 0
    SDL_memset(layout, 0, sizeof(VkForgeLayout));

    layout->surface = surface;
    layout->physical_device = physical_device;
    layout->device = device;
    return layout;
}}
"""
    return content.format()

def CreateDestroyForgeLayout(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_DestroyLayout(VkForgeLayout* forge_layout)
{{
    if ( forge_layout )
    {{
        // Destroy all pipelines
        for (uint8_t i = 0; i < VKFORGE_MAX_PIPELINES; i++)
        {{
            if(forge_layout->pipeline_buffer[i]) vkDestroyPipeline(forge_layout->device, forge_layout->pipeline_buffer[i], 0);
        }}

        // Destroy all pipeline layouts
        for (uint8_t i = 0; i < VKFORGE_MAX_PIPELINE_LAYOUTS; i++)
        {{
            // Destroy all descriptor sets and layouts
            for (uint8_t j = 0; j < forge_layout->descriptorset_layout_count[i]; j++)
            {{
                if(forge_layout->descriptorset_layout_buffer[i][j]) vkDestroyDescriptorSetLayout(forge_layout->device, forge_layout->descriptorset_layout_buffer[i][j], 0);
            }}
            if(forge_layout->pipeline_layout_buffer[i]) vkDestroyPipelineLayout(forge_layout->device, forge_layout->pipeline_layout_buffer[i], 0);
        }}

        SDL_free(forge_layout);
    }}
}}
"""
    return content.format()

def CreateFindPipelineFunction(ctx: VkForgeContext) -> str:
    content = """\
static const VkForgePipelineFunction* FindPipelineFunction(const char* pipeline_name)
{{
    for( uint32_t i = 0; i < VKFORGE_PIPELINE_FUNCTION_COUNT; i++ )
    {{
        if( strcmp(pipeline_name, VKFORGE_PIPELINE_FUNCTIONS[i]->pipeline_name) == 0 )
        {{
            return VKFORGE_PIPELINE_FUNCTIONS[i];
        }}
    }}
    return NULL;
}}
"""
    return content.format()

def CreateFindPipelineLayoutIndex(ctx: VkForgeContext) -> str:
    content = """\
static uint32_t FindPipelineLayoutIndex(const char* pipeline_name)
{{
    for( uint32_t i = 0; i < VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_count; i++ )
    {{
        if( strcmp(pipeline_name, VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_buffer[i]->pipeline_name) == 0 )
        {{
            return VKFORGE_REFERENCED_LAYOUT_DESIGN.reference_buffer[i]->pipeline_layout_design_index;
        }}
    }}
    return UINT32_MAX;
}}
"""
    return content.format()

def CreateBuildStageFlags(ctx: VkForgeContext) -> str:
    content = """\
static VkShaderStageFlags BuildStageFlags(const VkForgeLayoutBindDesign* bind)
{{
    if (!bind || bind->mode_count == 0) return 0;
    
    VkShaderStageFlags flags = bind->mode_buffer[0];
    for (uint32_t i = 1; i < bind->mode_count; i++)
    {{
        flags |= bind->mode_buffer[i];
    }}
    return flags;
}}
"""
    return content.format()

def CreateDescriptorSetLayoutBindings(ctx: VkForgeContext) -> str:
    content = """\
/// @brief
/// @param set_design
/// @param out_bindings Ensure it is large enough using VKFORGE_MAX_DESCRIPTOR_BINDINGS
/// @return
static void CreateDescriptorSetLayoutBindings(
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayoutBinding* out_bindings)
{{
    for (uint32_t j = 0; j < set_design->bind_design_count; j++)
    {{
        const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
        if( !bind ) continue;

        out_bindings[j] = (VkDescriptorSetLayoutBinding){{
            .binding = j,
            .descriptorType = bind->type,
            .descriptorCount = bind->count,
            .stageFlags = BuildStageFlags(bind)
        }};
    }}
}}
"""
    return content.format()

def CreateDescriptorSetLayout(ctx: VkForgeContext) -> str:
    content = """\
static VkResult CreateDescriptorSetLayout(
    VkDevice device,
    const VkForgeLayoutDescriptorSetLayoutDesign* set_design,
    VkDescriptorSetLayout* out_dsetLayout)
{{
    VkDescriptorSetLayoutBinding bindings[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {{0}};
    CreateDescriptorSetLayoutBindings(set_design, bindings);

    VkDescriptorSetLayoutCreateInfo setLayoutInfo = {{
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .bindingCount = CountDescriptorSetLayoutBindings(set_design),
        .pBindings = bindings
    }};

    VkResult result = vkCreateDescriptorSetLayout(device, &setLayoutInfo, NULL, out_dsetLayout);

    return result;
}}
"""
    return content.format()

def CreatePipelineLayout(ctx: VkForgeContext) -> str:
    content = """\
static VkResult CreatePipelineLayout(
    VkForgeLayout* forge_layout,
    const VkForgeLayoutPipelineLayoutDesign* pipeline_design,
    uint32_t pipeline_layout_index)
{{

    if( forge_layout->pipeline_layout_buffer[pipeline_layout_index] != VK_NULL_HANDLE )
    {{
        SDL_LogError(0, "Pipeline Layout already created");
        return VK_SUCCESS;
    }}

    if( pipeline_design->descriptorset_layout_design_count )
    {{
        for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
        {{
            const VkForgeLayoutDescriptorSetLayoutDesign* set_design = pipeline_design->descriptorset_layout_design_buffer[i];
            forge_layout->descriptorset_layout_count[pipeline_layout_index] = pipeline_design->descriptorset_layout_design_count;

            if(set_design->bind_design_count)
            {{
                VkResult result = CreateDescriptorSetLayout(forge_layout->device, set_design, &forge_layout->descriptorset_layout_buffer[pipeline_layout_index][i]);
                if (result != VK_SUCCESS)
                {{
                    SDL_LogError(0, "Failed to create descriptor set forge_layout");
                    for (uint32_t j = 0; j < i; j++)
                    {{
                        vkDestroyDescriptorSetLayout(forge_layout->device, forge_layout->descriptorset_layout_buffer[pipeline_layout_index][j], NULL);
                    }}
                    return result;
                }}
            }}
            else
            {{
                forge_layout->descriptorset_layout_buffer[pipeline_layout_index][i] = VK_NULL_HANDLE;
            }}
        }}
    }}

    VkPipelineLayoutCreateInfo layoutInfo = {{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = pipeline_design->descriptorset_layout_design_count,
        .pSetLayouts = forge_layout->descriptorset_layout_buffer[pipeline_layout_index],
        .pushConstantRangeCount = 0,
        .pPushConstantRanges = NULL
    }};

    VkPipelineLayout pipelineLayout;
    VkResult result = vkCreatePipelineLayout(forge_layout->device, &layoutInfo, NULL, &pipelineLayout);

    if (result != VK_SUCCESS)
    {{
        SDL_LogError(0, "Failed to create pipeline forge_layout");
        return result;
    }}

    // Store the created pipeline forge_layout
    forge_layout->pipeline_layout_buffer[pipeline_layout_index] = pipelineLayout;
    forge_layout->pipeline_layout_count ++;

    return VK_SUCCESS;
}}
"""
    return content.format()

def CreateForgePipeline(ctx: VkForgeContext) -> str:
    content = """\
VkResult VkForge_CreatePipeline(VkForgeLayout* forge_layout, const char* pipeline_name)
{{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Check if pipeline already exists
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {{
        SDL_LogError(0, "Pipeline creation function not found for %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }}

    if (forge_layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {{
        SDL_Log("Pipeline %s already exists", pipeline_name);
        return VK_SUCCESS;
    }}

    // Find the pipeline forge_layout index in the global design
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipeline_name);
    if (pipeline_layout_index == UINT32_MAX)
    {{
        SDL_LogError(0, "Pipeline forge_layout not found for %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }}

    // Create pipeline forge_layout if it doesn't exist
    if (forge_layout->pipeline_layout_buffer[pipeline_layout_index] == VK_NULL_HANDLE)
    {{
        const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
            VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

        VkResult result = CreatePipelineLayout(forge_layout, pipeline_design, pipeline_layout_index);
        if (result != VK_SUCCESS)
        {{
            return result;
        }}
    }}

    /// DYNAMIC RENDERING REQUIRED STRUCTURE ///
    VkSurfaceFormatKHR surfaceFormat = VkForge_GetSurfaceFormat(
        forge_layout->surface,
        forge_layout->physical_device,
        VKFORGE_DEFAULT_FORMAT
    );

    VkPipelineRenderingCreateInfo renderingInfo = {{0}};
    renderingInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO;
    renderingInfo.viewMask = 0;
    renderingInfo.colorAttachmentCount = 1;
    renderingInfo.pColorAttachmentFormats = &surfaceFormat.format;

    ///*************************************///

    // Create the pipeline
    VkPipeline pipeline = pipeline_func->CreatePipelineForFunc(
        NULL, // allocator
        &renderingInfo, // next Vulkan 1.3 dynamic rendering
        forge_layout->device,
        forge_layout->pipeline_layout_buffer[pipeline_layout_index]
    );

    if (pipeline == VK_NULL_HANDLE)
    {{
        SDL_LogError(0, "Failed to create pipeline %s", pipeline_name);
        return VK_ERROR_UNKNOWN;
    }}

    // Store the pipeline at its predefined index
    forge_layout->pipeline_buffer[pipeline_func->pipeline_index] = pipeline;
    forge_layout->pipeline_count ++;

    return VK_SUCCESS;
}}
"""
    return content.format()

def CreateBindPipeline(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_BindPipeline(VkForgeLayout* layout, const char* pipeline_name, VkCommandBuffer cmdbuf)
{{
    assert(layout);
    assert(pipeline_name);
    assert(layout->device);
    assert(cmdbuf);

    // Find the pipeline
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {{
        SDL_LogError(0, "Pipeline %s not found", pipeline_name);
        return;
    }}

    if (pipeline_func->pipeline_index < layout->pipeline_count &&
        layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {{
        vkCmdBindPipeline(
            cmdbuf, 
            VK_PIPELINE_BIND_POINT_GRAPHICS, 
            layout->pipeline_buffer[pipeline_func->pipeline_index]
        );
        return;
    }}

    SDL_LogError(0, "Pipeline %s not created", pipeline_name);
}}
"""
    return content.format()

def CreateCountDescriptorSetBinding(ctx: VkForgeContext) -> str:
    content = """\
static uint32_t CountDescriptorSetLayoutBindings(const VkForgeLayoutDescriptorSetLayoutDesign* set_design)
{{
    uint32_t count = 0;

    if(set_design->bind_design_count)
    {{
        for (uint32_t j = 0; j < set_design->bind_design_count; j++)
        {{
            const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
            if(bind) count ++;
        }}
    }}

    return count;
}}
"""
    return content.format()

def CreateBorrowPipeline(ctx: VkForgeContext) -> str:
    content = """\
/// @brief User must not free any resource returned
/// @param forge_layout
/// @param pipeline_name
/// @return
VkPipeline VkForge_BorrowPipeline(VkForgeLayout* forge_layout, const char* pipeline_name)
{{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Find the pipeline
    const VkForgePipelineFunction* pipeline_func = FindPipelineFunction(pipeline_name);
    if (!pipeline_func)
    {{
        SDL_LogError(0, "Pipeline %s not found", pipeline_name);
        return VK_NULL_HANDLE;
    }}

    if (pipeline_func->pipeline_index < forge_layout->pipeline_count &&
        forge_layout->pipeline_buffer[pipeline_func->pipeline_index] != VK_NULL_HANDLE)
    {{
        return forge_layout->pipeline_buffer[pipeline_func->pipeline_index];
    }}

    SDL_LogError(0, "Pipeline %s not created", pipeline_name);
    return VK_NULL_HANDLE;
}}
"""
    return content.format()

def CreateSharePipelineLayoutDetails(ctx: VkForgeContext) -> str:
    content = """\
/// @brief User must not free any resource returned.
/// @param forge_layout
/// @param pipeline_name
/// @param outPipelineLayouts
/// @param outDescriptorSetLayoutCount
/// @param outDescriptorSetLayouts  user must pass a buffer of VKFORGE_MAX_DESCRIPTORSET_LAYOUTS size
/// @param outDescriptorPoolSizeCount
/// @param outDescriptorPoolSizes  user must pass a buffer of VKFORGE_MAX_DESCRIPTOR_BINDINGS
void VkForge_SharePipelineLayoutDetails(
    VkForgeLayout* forge_layout,
    const char* pipeline_name,
    VkPipelineLayout* outPipelineLayouts,
    uint32_t* outDescriptorSetLayoutCount,
    VkDescriptorSetLayout* outDescriptorSetLayouts,
    uint32_t* outDescriptorPoolSizeCount,
    VkDescriptorPoolSize* outDescriptorPoolSizes
)
{{
    assert(forge_layout);
    assert(pipeline_name);
    assert(forge_layout->device);

    // Find the pipeline layout index
    uint32_t pipeline_layout_index = FindPipelineLayoutIndex(pipeline_name);
    if (pipeline_layout_index == UINT32_MAX)
    {{
        SDL_LogError(0, "Pipeline layout not found for %s", pipeline_name);
        exit(1);
    }}

    // Handle pipeline layout buffer requests
    if (outPipelineLayouts)
    {{
        outPipelineLayouts[0] = forge_layout->pipeline_layout_buffer[pipeline_layout_index];
    }}

    // Handle descriptor set layout count/buffer requests
    if (outDescriptorSetLayoutCount)
    {{
        *outDescriptorSetLayoutCount = forge_layout->descriptorset_layout_count[pipeline_layout_index];
    }}
    if (outDescriptorSetLayouts)
    {{
        for (uint32_t i = 0; i < forge_layout->descriptorset_layout_count[pipeline_layout_index]; i++)
        {{
            outDescriptorSetLayouts[i] = forge_layout->descriptorset_layout_buffer[pipeline_layout_index][i];
        }}
    }}

    // Handle descriptor pool size calculations
    if (outDescriptorPoolSizeCount || outDescriptorPoolSizes)
    {{
        const VkForgeLayoutPipelineLayoutDesign* pipeline_design =
            VKFORGE_REFERENCED_LAYOUT_DESIGN.pipeline_layout_design_buffer[pipeline_layout_index];

        uint32_t pool_size_count = 0;
        VkDescriptorPoolSize temp_pool_sizes[VKFORGE_MAX_DESCRIPTOR_BINDINGS] = {{0}};

        // First pass: calculate required pool sizes
        for (uint32_t i = 0; i < pipeline_design->descriptorset_layout_design_count; i++)
        {{
            const VkForgeLayoutDescriptorSetLayoutDesign* set_design =
                pipeline_design->descriptorset_layout_design_buffer[i];

            if (!set_design) continue;

            for (uint32_t j = 0; j < set_design->bind_design_count; j++)
            {{
                const VkForgeLayoutBindDesign* bind = set_design->bind_design_buffer[j];
                if (!bind) continue;

                bool found = false;
                for (uint32_t k = 0; k < pool_size_count; k++)
                {{
                    if (temp_pool_sizes[k].type == bind->type)
                    {{
                        temp_pool_sizes[k].descriptorCount += bind->count;
                        found = true;
                        break;
                    }}
                }}

                if (!found)
                {{
                    temp_pool_sizes[pool_size_count].type = bind->type;
                    temp_pool_sizes[pool_size_count].descriptorCount = bind->count;
                    pool_size_count++;
                }}
            }}
        }}

        // Return the count if requested
        if (outDescriptorPoolSizeCount)
        {{
            *outDescriptorPoolSizeCount = pool_size_count;
        }}

        // Return the actual pool sizes if requested
        if (outDescriptorPoolSizes)
        {{
            for (uint32_t i = 0; i < pool_size_count; i++)
            {{
                outDescriptorPoolSizes[i] = temp_pool_sizes[i];
            }}
        }}
    }}
}}
"""
    return content.format()

def GetLayoutStrings(ctx: VkForgeContext):
    return [
        CreateForgeReferencedLayoutDesign(ctx),
        CreateForgeLayout(ctx),
        CreatePipelineFunctionStruct(ctx),
        CreateCreateForgeLayout(ctx),
        CreateDestroyForgeLayout(ctx),
        CreateFindPipelineFunction(ctx),
        CreateFindPipelineLayoutIndex(ctx),
        CreateBuildStageFlags(ctx),
        CreateCountDescriptorSetBinding(ctx),
        CreateDescriptorSetLayoutBindings(ctx),
        CreateDescriptorSetLayout(ctx),
        CreatePipelineLayout(ctx),
        CreateForgePipeline(ctx),
        CreateBindPipeline(ctx),
        CreateBorrowPipeline(ctx),
        CreateSharePipelineLayoutDetails(ctx)
        
    ]