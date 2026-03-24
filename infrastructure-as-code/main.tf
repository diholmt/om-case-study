resource "local_file" "foo" {
  for_each = var.files_map
  content  = "# Some content for file ${each.value.index}"
  filename = "file${each.value.index}.txt"
}
