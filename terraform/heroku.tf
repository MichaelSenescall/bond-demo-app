resource "heroku_app" "bond_demo_app" {
  name   = "bond-demo-app"
  stack  = "container"
  region = "us"
}

resource "heroku_build" "bond_demo_app_build" {
  app = heroku_app.bond_demo_app.id

  source {
    path = "../app"
  }
}