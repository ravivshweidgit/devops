include "root" {
  path = find_in_parent_folders()
}

dependency "vpc" {
  config_path = "../../vpc/dev"
}

terraform {
  source = "../../../../modules/ec2"
}

inputs = {
  environment        = "dev"
  vpc_id            = dependency.vpc.outputs.vpc_id
  public_subnet_id  = dependency.vpc.outputs.public_subnet_ids[0]  # Use first public subnet
  public_key        = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCI2iUIZubvCZgs59KSOKjNXEMVEEFJQhh3k9tJ29Qu/lApjq9ptJ2sGeSbjLi1z5sqvh/D1SFS7a0HeBeRqdH9msfTZ8BBZMQBj15qZCaNA2FMfWxLxW6LW4JI3U6bx/thr4HESufdO/KCsLDMi28mlgnc2xkPxrCnhQHRVN3eq+sX7YhQrbct6lxl293NIot1ttpT6p6yhqT2OzFrdw8duG9fpcmTn09ftATezehDjMsiNF7GsmJ4enex9XLXwJPiOlOGt9pk9VsHJgDKeVn0KjdEjaVrVA8Ihw3dA4gQjWerPkH53YQYEVjmM49wKdrg1dA2uBhQHnBysSn9V+dZ bastion-key"
}
