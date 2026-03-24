variable "files_map" {
  description = "Map of files to create with stable identifiers"
  type = map(object({
    index = number
  }))
  default = {
    "file0" = { index = 0 }
    "file1" = { index = 1 }
    "file2" = { index = 2 }
    "file3" = { index = 3 }
    "file4" = { index = 4 }
  }
}