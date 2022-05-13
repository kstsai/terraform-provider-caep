package caep

import (
	"context"
	//"crypto/tls"
	"encoding/json"
	"fmt"
	//"io/ioutil"
	"log"
	//"regexp"
	"strings"
	//"net/http"
	//"time"

	"github.com/hashicorp/terraform-plugin-sdk/v2/diag"
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
)

func dataSourceCaep() *schema.Resource {

	return &schema.Resource{
		// This description is used by the documentation generator and the language server.
		Description: "Sample data source in the Terraform provider scaffolding.",

		ReadContext: dataSourceCaepGeneric,

		Schema: map[string]*schema.Schema{
			"filter_pattern": {
				// This description is used by the documentation generator and the language server.
				Description: "CAEP data filter, supported values : apptemplate, vminstance, dkinstance",
				Type:        schema.TypeString,
				Required:    true,
			},
			"worker_ip": {
				// This description is used by the documentation generator and the language server.
				Description: "CAEP data filter, supported values : apptemplate, vminstance, dkinstance",
				Type:        schema.TypeString,
				Optional:    true,
				DefaultFunc: schema.EnvDefaultFunc("DATA_WORKER_IP", "ALL"),
			},
			"aio_show_deployable_apps": &schema.Schema{
				Type:        schema.TypeBool,
				Optional:    true,
				DefaultFunc: schema.EnvDefaultFunc("SHOW_APP_INSTANCES", false),
			},

			"backable_host": &schema.Schema{
				Type:        schema.TypeString,
				Optional:    true,
				DefaultFunc: schema.EnvDefaultFunc("SHOW_APP_INSTANCES", false),
			},
			EGNODEHOST: &schema.Schema{
				Type:     schema.TypeList,
				Computed: true,
				Elem: &schema.Resource{
					Schema: map[string]*schema.Schema{
						"aio_ip": &schema.Schema{
							Type:     schema.TypeString,
							Required: true,
						},
						"aio_brief": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"aio_extra": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"aio_backup_vol": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"app_templates": &schema.Schema{
							Type:     schema.TypeList,
							Computed: true,
							Elem: &schema.Resource{
								Schema: map[string]*schema.Schema{
									"app_name": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"app_type": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"flavor": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									/*
										"app_id": &schema.Schema{
											Type:     schema.TypeString,
											Computed: true,
										},
										"app_extra": &schema.Schema{
											Type:     schema.TypeString,
											Computed: true,
										},
									*/
								},
							},
						},
						"service_instances": &schema.Schema{
							Type:     schema.TypeList,
							Computed: true,
							Elem: &schema.Resource{
								Schema: map[string]*schema.Schema{
									"aio_ip": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"service_name": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"app_id": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"state": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"urn_key": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"notify_key": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
								},
							},
						},
						"app_deployable": &schema.Schema{
							Type:     schema.TypeList,
							Computed: true,
							Elem: &schema.Resource{
								Schema: map[string]*schema.Schema{
									"app_name": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"app_type": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"flavor": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
								},
							},
						},
					},
				},
			},
		},
	}
}

type EdgeServiceTemplate struct {
	AppName  string `json:"app_name,omitempty"`
	AppType  string `json:"app_type,omitempty"`
	Flavor   string `json:"flavor,omitempty"`
	AppExtra string `json:"app_extra,omitempty"`
}

type EdgeServiceInstance struct {
	AioIp       string `json:"aio_ip"`
	ServiceName string `json:"service_name,omitempty"`
	AppId       string `json:"app_id,omitempty"`
	State       string `json:"state,omitempty"`
	UrnKey      string `json:"urn_key",omitempty"`
	NotifyKey   string `json:"notify_key",omitempty"`
	//AppManagementIp string `json:"mgmt_ip,omitempty"`
	//AppVnics        string `json:"vnics,omitempty"`
	//Status          string `json:"status,omitempty"`
	//AppExtra string `json:"app_extra,omitempty"`
}

type WorkerHostBrief struct {
	AioIp        string `json:"aio_ip"`
	AioBrief     string `json:"aio_brief"`
	AioExtra     string `json:"aio_extra"`
	AioBackupVol string `json:"aio_backup_vol"`

	EdgeServiceTemplates []EdgeServiceTemplate `json:"app_templates,omitempty"`
	EdgeServiceInstances []EdgeServiceInstance `json:"service_instances,omitempty"`
	EdgeDeployableApps   []EdgeServiceTemplate `json:"app_deployable,omitempty"` // == AllAppTempl - AllDeployedAppInst
}

func dataSourceCaepGeneric(ctx context.Context, d *schema.ResourceData, meta interface{}) (diags diag.Diagnostics) {
	// use the meta value to retrieve your client from the provider configure method
	m := meta.(apiClient)

	//http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	//client := &http.Client{Timeout: 10 * time.Second}
	workerIp := d.Get("worker_ip").(string)
	_, workerIpInList := m.AppRunHostMap[workerIp]
	if !workerIpInList {
		log.Printf("[INFO] input worker_ip %s not in pre-confiured list, IGNORED\n", workerIp)
	}

	filter_ptn := d.Get("filter_pattern").(string)
	d.SetId(fmt.Sprintf("%s %s", workerIp, filter_ptn))

	switch filter_ptn {
	case "worker_brief":
		whjson := make([]WorkerHostBrief, 0)
		for _, hm := range m.AppRunHostMap {

			if !workerIpInList && workerIp != "all" {
				break
			}

			if workerIpInList && workerIp != hm.EghostIp {
				continue
			}

			var whb WorkerHostBrief
			whb.AioIp = hm.EghostIp

			uri := fmt.Sprintf("http://%s:10288/compute/usable", hm.EghostIp)
			apiRes0, _ := CaepApiComputeUsable(m, uri)

			whb.AioBrief = fmt.Sprintf("remaining vCPU: %d, Mem Pages: %dG, apps home (GB): %d",
				apiRes0.VcpuTotal-apiRes0.VcpuUsed,
				apiRes0.HugepageTotalGb-apiRes0.HugepageUsedGb,
				apiRes0.HomeDiskTotalGb-apiRes0.HomeDiskUsedGb)
			if apiRes0.BackDiskInfo != "" && strings.Contains(apiRes0.BackDiskInfo, "not found") == false {
				whb.AioBackupVol = apiRes0.BackDiskInfo
				d.Set("backable_host", hm.EghostIp)
			}
			whb.AioExtra = hm.HwResources

			// get ALL deployed app instances
			appDeployed := make(map[string]*EdgeServiceInstance)
			uri = fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/nodes/%s/apps", hm.EghostIp, hm.EgNodeId)
			apiRes2, _ := CaepApiGet(m, hm, uri)
			appInstances := apiRes2.Data.([]interface{})
			for _, it := range appInstances {
				inst := it.(map[string]interface{})

				appDeployed[inst["app_name"].(string)] = &EdgeServiceInstance{
					ServiceName: inst["app_name"].(string),
					AppId:       inst["app_id"].(string),
					State:       inst["state"].(string),
				}
			}

			uri_eaaServices := fmt.Sprintf("http://%s:10282/eaa/services?ItsUrBoss=true", hm.EghostIp)
			eaaSvcs, _ := CaepApiEaaServices(m, uri_eaaServices)
			whb.EdgeServiceInstances = make([]EdgeServiceInstance, 0)
			for _, eas := range eaaSvcs.Services {
				appName := eas.Notifications[0].Name // TODO: have space to improve
				eai := EdgeServiceInstance{ServiceName: appName,
					UrnKey:    fmt.Sprintf("id=%s,namespace=%s", eas.Urn.ID, eas.Urn.Namespace),
					NotifyKey: fmt.Sprintf("name=%s,version=%s", eas.Notifications[0].Name, eas.Notifications[0].Version),
					AioIp:     hm.EghostIp,
					State:     appDeployed[appName].State,
					AppId:     appDeployed[appName].AppId,
				}
				whb.EdgeServiceInstances = append(whb.EdgeServiceInstances, eai)
			}

			if d.Get("aio_show_deployable_apps").(bool) == true {

				// get ALL available app templates
				allAppTemplates := make([]EdgeServiceTemplate, 0)
				uri = fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/templates", hm.EghostIp)
				apiRes, _ := CaepApiGet(m, hm, uri)
				appTemplates := apiRes.Data.([]interface{})
				for _, it := range appTemplates {
					templ := it.(map[string]interface{})
					allAppTemplates = append(allAppTemplates, EdgeServiceTemplate{
						AppType: templ["app_type"].(string),
						AppName: templ["template_name"].(string),
						Flavor:  templ["flavor"].(string),
					})
				}

				// get deployable app templates = all-app-templates - deployed-app-instances
				whb.EdgeDeployableApps = make([]EdgeServiceTemplate, 0)
				for _, templ := range allAppTemplates {
					if _, existed := appDeployed[templ.AppName]; !existed {
						whb.EdgeDeployableApps = append(whb.EdgeDeployableApps, EdgeServiceTemplate{
							AppName: templ.AppName,
							AppType: templ.AppType,
							Flavor:  templ.Flavor,
						})
					}
				}
			} else {
				whb.EdgeDeployableApps = nil
			}
			whjson = append(whjson, whb)
		}

		retWhs := make([]map[string]interface{}, 0)
		byts, _ := json.Marshal(whjson)
		json.Unmarshal(byts, &retWhs)
		if err := d.Set(EGNODEHOST, retWhs); err != nil {
			return diag.FromErr(err)
		}
	}
	return diags
}
