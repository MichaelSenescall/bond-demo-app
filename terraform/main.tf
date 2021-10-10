terraform {
  backend "remote" {
    organization = "MichaelSenescall"

    workspaces {
      name = "bond-demo-app"
    }
  }
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "4.6.0"
    }
  }
}

provider "heroku" {}