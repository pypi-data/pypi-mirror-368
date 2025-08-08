# VkForge

**VkForge** (Vulkan Forge) is a **Vulkan User-End API Implementation Generator** written in **Python**. It's purpose is to quickly generate the code needed for Graphics Renderer development.

VkForge is the opposite of using a wrapper layer (like SDL_GPU or shVulkan).  
Instead of abstracting Vulkan, you use the **Vulkan API directly** — but VkForge saves you from writing all the repetitive boilerplate by generating it for you, based on your **shaders** and a simple **config**.

VkForge does not force any design pattern — you have the same freedom as hand-written Vulkan.  
By design, VkForge does not generate an entire renderer — it generates **components** for you to connect as you wish.

VkForge also provides a list of utility code that makes it quicker to code in Vulkan. If the utility function
abstracts away something you want to control, just use the direct Vulkan function.

---

## VkForge Source

The input for VkForge is:
- **Shaders:** Provide type, location, descriptor sets, and bindings.
- **Config:** Defines pipeline details and other setup.

---

## VkForge Output

VkForge generates **C99 source code** for your Vulkan implementation.  
Platform integration is done via **SDL3**.
We are hoping to improve VkForge — see [CONTRIBUTING.md](CONTRIBUTING.md).
Feel free to contribute by using it, reporting issues, making pull requests and via othe produtive ways!

---

## Todo

- [ ] Add support for Renderpass and earlier versions: Currently only support Vulkan >= 1.3 and Dynamic Rendering. 
- [ ] Platform abstraction: Allow users to pass a flag `vkforge --platform SDL3` with options like `Raylib`, `GLFW`, etc. VkForge will generate the code specific for the platform you want.
- [ ] Sub-Platform abstraction: I can combined SDL3 as my main platform and then use SDL3_image, stb_image, etc to load images and so on. `vkforge --platform-image SDL3_image`.
- [ ] 3D utility functions: Utility functions specific for 3D rendering
- [ ] Extended version utility functions: Extended utility functions provide additional parameters that allow the user to pass pNext and pAllocationCallbacks.

---

## Connections

[VkForge Python Package](https://pypi.org/project/vkforge/)
[VkForge Github](https://github.com/Rickodesea/VkForge)

---

## Purpose

Vulkan is extremely detailed — this is a good thing!  
But it can mean tedious and repetitive coding.  
VkForge solves this by letting you describe your Vulkan setup in a simple Config file.  
A config is short, easy to write, and saves hours of manual work.

---

## Closing

VkForge is free and MIT licensed — contributions are welcome!  
I hope you find it useful for your projects.

VkForge is led and maintained by its benevolent leader, Alrick Grandison.

(c) 2025 Alrick Grandison, Algodal
