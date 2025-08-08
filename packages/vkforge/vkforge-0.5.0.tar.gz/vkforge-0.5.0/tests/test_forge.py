from vkforge import VkForgeModel
import yaml

yml_string = """
Pipeline:
  - name: my_pipeline
    ShaderModule:
      - path: vert.spv
        mode: vert
      - path: frag.spv
        mode: frag
    VertexInputBindingDescription:
      - stride: Vertex
        first_location: 0
"""

# yml_path = Path(__file__).parent / "fixtures" / "my_config.yml"
# raw_data = yaml.safe_load(yml_path.read_text())


def test_forge_config():
    raw_data = yaml.safe_load(yml_string)
    forgeConfig = VkForgeModel(**raw_data)

    assert forgeConfig.namespace == "basic_renderer_"
    assert forgeConfig.namestyle == "snake_case"
    assert isinstance(forgeConfig.Pipeline, list)
