terraform {
  required_providers {
    caep = {
      version = "~> 0.1"
      source  = "hashicorp.com/edu/caep"
    }
  }
}

provider "caep" {
  aio_workers {
    #worker {
    #  aio_ip = "192.168.82.10"
    #  aio_user = "user"
    #  aio_pass = "123456"
    #}
    worker {
      aio_ip = "192.168.82.35"
    }
    #worker {
    #  aio_ip = "192.168.82.37"
    #}
    worker {
      aio_ip = "192.168.82.39"
    }
    #worker {
    #  aio_ip = "192.168.82.87"
    #}
    #worker {
    #  aio_ip = "192.168.82.229"
    #}
  }
}

data "caep_edgehost" "all" {
  filter_pattern = "worker_brief"
  worker_ip = "all"
  aio_show_deployable_apps = false 
}

output "outWorkerBrief1" {
  value = data.caep_edgehost.all
}


resource "caep_edgesvc" "egsvc1" {
  app_name = "secure-dkvm"
  worker_ip = "192.168.82.39"
  #action = "stop"
  app_backup = true
  pci_addr_csv = "pt-net82" 
}

output "svc1" {
  value = caep_edgesvc.egsvc1
}

resource "caep_edgesvc" "egsvc2" {
  app_name = "uevm32"
  worker_ip = "192.168.82.39"
  #action = "stop"
  app_backup = true
  pci_addr_csv = "pt-net82" 
}

output "svc2" {
  value = caep_edgesvc.egsvc2
}

/*
resource "caep_edgesvc" "sgsvcex2" {
  app_name = "free5gc-compose"
  worker_ip = "192.168.82.236"
  action = "start"
}
output "sgsvc2" {
  value = caep_edgesvc.sgsvcex2
  worker_ip = "192.168.82.236"
}
resource "caep_edgesvc" "egsvc3" {
  app_name = "secvm"
  worker_ip = "192.168.82.33"
}

output "svc3" {
  value = caep_edgesvc.egsvc3
}
*/
