from vkforge.context import VkForgeContext
from vkforge.mappings import *
from .core import GetCoreStrings
from .pipeline import GetPipelineStrings
from .util import GetUtilStrings
from .layout import GetLayoutStrings
import re

def CreateVoidEnum(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_VOID_ENUM(Var, Type, Func, Sizelimit, ...) \\
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \\
    Func(__VA_ARGS__, &Var##_count, 0); \\
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \\
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \\
}} while(0)
"""
    output = content.format()

    return output

def CreateEnum(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_ENUM(Var, Type, Func, Sizelimit, ...) \\
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \\
    Func(__VA_ARGS__, &Var##_count, 0); \\
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \\
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \\
}} while(0)
"""
    output = content.format()

    return output

def extract_function_declarations(content: str) -> list[str]:
    """Extract all function declarations using regex."""
    # This pattern matches:
    # 1. Return type (any valid C type with pointers/qualifiers)
    # 2. Function name
    # 3. Parameters (including varargs and function pointers)
    # 4. Stops at opening brace (ignoring attributes)
    pattern = r"""
        ^\s*                          # Start of line with possible whitespace
        (                             # Capture group 1: return type
            (?:                       
                [a-zA-Z_]\w*          # Basic type (int, char, etc.)
                (?:\s*\*?\s*const)?   # Optional pointer/const qualifiers
                \s+                   # Requires whitespace after type
            )+
        )
        ([a-zA-Z_]\w*)                # Capture group 2: function name
        \s*                           # Optional whitespace
        \(                            # Opening paren
        ([^)]*)                       # Capture group 3: parameters
        \)                            # Closing paren
        \s*                           # Optional whitespace
        (?:                           # Non-capturing group for attributes
            \s*__attribute__\s*\(\([^)]*\)\)  
        )*
        \s*                           # Optional whitespace
        (?={)                         # Lookahead for opening brace
    """
    functions = []
    
    for match in re.finditer(pattern, content, re.VERBOSE | re.MULTILINE):
        return_type = match.group(1).strip()
        name = match.group(2).strip()
        params = match.group(3).strip()

        if 'static ' in return_type:
            continue
        
        # Reconstruct declaration
        decl = f"{return_type} {name}({params});"
        functions.append(decl)
    
    return functions

def CreateDeclarations(ctx: VkForgeContext) -> str:
    """Generate ONLY function forward declarations using robust regex parsing."""
    declarations = "// Function Declarations\n\n"
    
    # Collect all content from all modules
    all_content = []
    all_content.extend(GetCoreStrings(ctx))
    all_content.extend(GetUtilStrings(ctx))
    all_content.extend(GetPipelineStrings(ctx))
    all_content.extend(GetLayoutStrings(ctx))
    
    # Process each content block
    for content in all_content:
        for decl in extract_function_declarations(content):
            declarations += decl + "\n\n"
    
    return declarations

def GetFuncStrings(ctx: VkForgeContext):
    return [
        CreateEnum(ctx),
        CreateVoidEnum(ctx),
        CreateDeclarations(ctx)
    ]