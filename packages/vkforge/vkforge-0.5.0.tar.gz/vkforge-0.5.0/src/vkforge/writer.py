import os
from pathlib import Path
from vkforge.context import VkForgeContext
from vkforge.translators import *
from vkforge.mappings import *

TYPE_INCLUDE = f'#include "{FILE.TYPE}"'
FUNC_INCLUDE = f'#include "{FILE.FUNC}"'

def IncludeStandardDefinitionHeaders():
    return """\
#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>
"""

def IncludeStandardDeclarationHeaders():
    return """\
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
"""

def Write_Plain_File(ctx: VkForgeContext, filename, stringFunc):
    output = "\n".join(stringFunc(ctx))

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if (
        ctx.forgeModel.GenerateOnce 
        and filename in ctx.forgeModel.GenerateOnce 
        and filepath.exists()
    ):
        print(f"SKIPPED (GenerateOnce): {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(output)
            print(f"GENERATED: {filepath}")


def Write_C_Definition_Module(ctx: VkForgeContext, filename, stringFunc):
    content = """\
{standard_includes}
{type_include}
{func_include}

{user_defined_includes}
{user_defined_insertions}

{code}

"""
    output = content.format(
        standard_includes=IncludeStandardDefinitionHeaders(),
        type_include=TYPE_INCLUDE,
        func_include=FUNC_INCLUDE,
        user_defined_includes=GetUserDefinedIncludes(ctx),
        user_defined_insertions=GetUserDefinedInsertions(ctx),
        code="\n".join(stringFunc(ctx)),
    )

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if (
        ctx.forgeModel.GenerateOnce 
        and filename in ctx.forgeModel.GenerateOnce 
        and filepath.exists()
    ):
        print(f"SKIPPED (GenerateOnce): {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(output)
            print(f"GENERATED: {filepath}")


def Write_C_Declaration_Module(ctx: VkForgeContext, filename, stringFunc):
    content = """\
#pragma once

{standard_includes}
{forge_includes}

#ifdef __cplusplus
extern "C" {{
#endif

{code}

#ifdef __cplusplus
}}
#endif
"""
    forge_includes = ""
    if filename != FILE.TYPE:
        forge_includes += f"#include \"{FILE.TYPE}\""
    
    output = content.format(
        standard_includes=IncludeStandardDeclarationHeaders(),
        forge_includes=forge_includes,
        code="\n".join(stringFunc(ctx)),
    )

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if (
        ctx.forgeModel.GenerateOnce 
        and filename in ctx.forgeModel.GenerateOnce 
        and filepath.exists()
    ):
        print(f"SKIPPED (GenerateOnce): {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(output)
            print(f"GENERATED: {filepath}")

def GetUserDefinedIncludes(ctx: VkForgeContext) -> str:
    if ctx.forgeModel.UserDefined:
        if ctx.forgeModel.UserDefined.includes:
            includes = []
            for header in ctx.forgeModel.UserDefined.includes:
                if header.startswith('<') and header.endswith('>'):
                    includes.append(f"#include {header}")
                else:
                    includes.append(f'#include "{header}"')
            
            return '\n'.join(includes) + '\n'
    return "/** NO USER INCLUDES **/"

def GetUserDefinedInsertions(ctx: VkForgeContext) -> str:
    if ctx.forgeModel.UserDefined:
        if ctx.forgeModel.UserDefined.insertions:
            insertions = ctx.forgeModel.UserDefined.insertions
            return '\n'.join(insertions) + '\n'
    return "/** NO USER DECLARATIONS **/"

def Generate(ctx: VkForgeContext):
    Write_C_Definition_Module(ctx, FILE.CORE, GetCoreStrings)
    Write_C_Definition_Module(ctx, FILE.UTIL, GetUtilStrings)
    Write_C_Definition_Module(ctx, FILE.LAYOUT, GetLayoutStrings)
    Write_C_Definition_Module(ctx, FILE.PIPELINE_C, GetPipelineStrings)
    Write_C_Declaration_Module(ctx, FILE.TYPE, GetTypeStrings)
    Write_C_Declaration_Module(ctx, FILE.FUNC, GetFuncStrings)
    Write_Plain_File(ctx, FILE.CMAKE, GetCMakeStrings)
