variable "datetime_tag" {
  default = formatdate("YYYYMMDD-hhmmss", timestamp())
}

group "default" {
  targets = ["default"]
}

target "default" {
  context = "."
  dockerfile = ".devcontainer/Dockerfile"
  target = "default"
  tags = ["4alonkellner/ties-ci:${datetime_tag}", "4alonkellner/ties-ci:latest"]
  output = [{ type = "registry" }]
  platforms = ["linux/amd64", "linux/arm64"]
}
