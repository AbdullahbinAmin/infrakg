from pathlib import Path
from infrakg.parsers.terraform import TerraformParser
from infrakg.cli import build_graph_from_dir
from infrakg.parsers.base import ParserPlugin

def test_terraform_parser(tmp_path: Path):
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('''
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
}
''')
    
    parser = TerraformParser()
    nodes, edges = parser.parse(tmp_path)
    
    assert len(nodes) == 2
    assert len(edges) == 1
    assert edges[0].source_id == "aws_subnet.public"
    assert edges[0].target_id == "aws_vpc.main"

def test_cli_build_graph(tmp_path: Path):
    # Tests that the high-level builder works
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('resource "aws_vpc" "main" {}')
    
    graph = build_graph_from_dir(tmp_path)
    assert "aws_vpc.main" in graph.graph
