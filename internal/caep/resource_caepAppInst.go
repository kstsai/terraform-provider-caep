package caep

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/hashicorp/terraform-plugin-sdk/v2/diag"
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
)

func resourceCaepAppInst() *schema.Resource {

	return &schema.Resource{
		// This description is used by the documentation generator and the language server.
		Description: "resource AppInst (deployed EdgeApp) in the Terraform provider caep.",

		CreateContext: resourceCaepAppInstCreate,
		ReadContext:   resourceCaepAppInstRead,
		UpdateContext: resourceCaepAppInstUpdate,
		DeleteContext: resourceCaepAppInstDelete,
		Schema: map[string]*schema.Schema{
			"worker_ip": {
				// This description is used by the documentation generator and the language server.
				Description: "To match EdgeAppTemplate.template_name for deplpoyment",
				Type:        schema.TypeString,
				Required:    true,
			},
			"app_name": {
				// This description is used by the documentation generator and the language server.
				Description: "To match EdgeAppTemplate.template_name for deplpoyment",
				Type:        schema.TypeString,
				Required:    true,
			},
			"action": &schema.Schema{
				Type:     schema.TypeString,
				Optional: true,
				Default:  "auto-start",
			},
			"app_backup": &schema.Schema{
				Type:     schema.TypeBool,
				Optional: true,
				Default:  false,
			},
			"pci_addr_csv": &schema.Schema{
				Type:     schema.TypeString,
				Optional: true,
				Computed: true,
			},
			/*"app_type": &schema.Schema{
										Type:     schema.TypeString,
										Optional: true,
										Computed: true,
						        },
						"status": {
							// This description is used by the documentation generator and the language server.
							Description: "Edge App Instance status",
							Type:        schema.TypeString,
							Optional:    true,
							Computed:    true,
			        },*/
			"worker_extra": {
				// This description is used by the documentation generator and the language server.
				Description: "To match EdgeAppTemplate.template_name for deplpoyment",
				Type:        schema.TypeString,
				Computed:    true,
			},
			"app_extra": {
				// This description is used by the documentation generator and the language server.
				Description: "Edge App runtime info ",
				//Type:        schema.TypeString,
				Type: schema.TypeList,
				Elem: &schema.Resource{
					Schema: map[string]*schema.Schema{
						"app_type": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"flavor": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"state": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"mgmt_ip": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
						"vnics": &schema.Schema{
							Type:     schema.TypeString,
							Computed: true,
						},
					},
				},
				Optional: true,
				Computed: true,
			},
		},
	}
}

type appExtraSt struct {
	AppType         string `json:"type,omitempty"`
	Flavor          string `json:"flavor,omitempty"`
	State           string `json:"state,omitempty"`
	AppManagementIp string `json:"mgmt_ip,omitempty"`
	Vnics           string `json:"vnics,omitempty"`
}

type CaepAppInstExt struct {
	AppType         string `json:"app_type,omitempty"`
	State           string `json:"state,omitempty"`
	AppManagementIp string `json:"mgmt_ip,omitempty"`
	AppVnics        string `json:"vnics,omitempty"`
	//Status          string `json:"status,omitempty"`
	Flavor string `json:"flavor,omitempty"`
}

func resourceCaepAppInstCreate(ctx context.Context, d *schema.ResourceData, meta interface{}) diag.Diagnostics {
	// use the meta value to retrieve your client from the provider configure method
	// client := meta.(*apiClient)
	var diags diag.Diagnostics

	m := meta.(apiClient)
	workerIp := d.Get("worker_ip").(string)
	//var hm caepHostInfo
	hm, ok := m.AppRunHostMap[workerIp]
	if !ok {
		return diag.Errorf("invalid worker_ip %s %v", workerIp, hm)
	}
	//m.ApiToken = hm.ApiToken

	log.Printf("[DEBUG]  %+v hm %+v", m.AppRunHostMap, hm)

	uri := fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/templates", hm.EghostIp)
	apiRes, _ := CaepApiGet(m, hm, uri)
	//appTemplates := apiRes.Data.([]map[string]interface{})
	appTemplates := apiRes.Data.([]interface{})
	type appTemplSt struct {
		AppType      string
		TemplateId   string
		TemplateName string
		Flavor       string
	}

	availAppTemplates := make(map[string]appTemplSt)
	for _, apptempl := range appTemplates {
		templ := apptempl.(map[string]interface{})
		appName := templ["template_name"].(string)
		availAppTemplates[strings.TrimSpace(appName)] = appTemplSt{AppType: templ["app_type"].(string),
			Flavor:       templ["flavor"].(string),
			TemplateId:   templ["template_id"].(string),
			TemplateName: templ["template_name"].(string),
		}
	}
	/*appConfig := make(map[string]string) /*struct {
			Flavor     string
			InternalIp string
	}*/
	tname := d.Get("app_name").(string)
	if appTemplate, valid := availAppTemplates[tname]; valid {

		appId := appTemplate.TemplateId
		d.SetId(appId)

		retAppExt := make(map[string]interface{}, 0)
		byts, _ := json.Marshal(appExtraSt{Flavor: appTemplate.Flavor,
			AppType: appTemplate.AppType})

		json.Unmarshal(byts, &retAppExt)

		d.Set("app_extra", retAppExt)

		d.Set("worker_extra", fmt.Sprintf("%s(%s)/node_id=%s", hm.EghostIp, hm.EghostDns, hm.EgNodeId))
		//d.Set("status", "deploying")
		//appConfig["flavor"] = appTemplate.Flavor
		//d.Set("config", appTemplate.Flavor)
		//d.Set("config", appConfig)
		//d.Set("app_type", appTemplate.AppType)
		//attr1 := d.Get("sample_attribute").(string)
		pd := map[string]string{"template_id": appTemplate.TemplateId}
		uri := fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/nodes/%s/apps", hm.EghostIp, hm.EgNodeId)
		caepRes, _ := CaepApiPost(m, hm, uri, pd)
		log.Printf("[DEBUG] resourceCaepAppInstCreate %+v resp of uri %s", caepRes, uri)
		if caepRes.ErrCode != 0 {
			return diag.Errorf("resource %s to create at %s failed because of %+v", tname, workerIp, caepRes)
		}

		time.Sleep(1 * time.Second)

		isAppBackupEnable := d.Get("app_backup")
		log.Printf("[DEBUG] resourceCaepAppInstCreate isAppBackup %v %s", isAppBackupEnable, m.BackupAioIp)
		if isAppBackupEnable != nil && isAppBackupEnable.(bool) && m.BackupAioIp != "" {
			uri := fmt.Sprintf("http://%s:10288/apps/%s/backup?backup_host_ip=%s", hm.EghostIp,
				appId,
				m.BackupAioIp)
			caepRes, _ := CaepApiPut(m, hm, uri, map[string]string{})
			log.Printf("[DEBUG] resourceCaepAppInstCreate %+v resp of uri %s", caepRes, uri)
		}
		resourceCaepAppInstRead(ctx, d, m)
	} else {
		d.SetId("invalid")
		//d.Set("status", "not deployed")
	}
	return diags
}

func resourceCaepAppInstRead(ctx context.Context, d *schema.ResourceData, meta interface{}) (diags diag.Diagnostics) {
	// use the meta value to retrieve your client from the provider configure method
	// client := meta.(*apiClient)
	m := meta.(apiClient)

	workerIp := d.Get("worker_ip").(string)
	hm, ok := m.AppRunHostMap[workerIp]
	if !ok {
		return diag.Errorf("invalid worker_ip %s %v", workerIp, hm)
	}
	//m.ApiToken = hm.ApiToken

	app_act := d.Get("action").(string)
	uri := fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/nodes/%s/apps/%s", hm.EghostIp, hm.EgNodeId, d.Id())
	log.Printf("[DEBUG] resourceCaepAppInstRead %s app_id=%s", uri, d.Id())
	apiRes, _ := CaepApiGet(m, hm, uri)
	if apiRes.Data == nil {
		log.Printf("[ERROR] resourceCaepAppInstRead %+v", apiRes)
		/*diags = append(diags, diag.Diagnostic{
					Severity: diag.Error,
					Summary:  fmt.Sprintf("[ERROR] resourceCaepAppInstRead %+v", apiRes),
		    })*/
		return // diag.Errorf("invalid (not found) app_id %s %+v", d.Id(), hm)
	}
	inst := apiRes.Data.(map[string]interface{})
	log.Printf("[DEBUG] resourceCaepAppInstRead %+v", inst)
	app_id := inst["app_id"].(string)
	app_state := inst["state"].(string)
	if app_id != d.Id() {
		log.Printf("[ERROR] resourceCaepAppInstRead %+v id mismatch %s != %d", apiRes, app_id, d.Id())
		/*diags = append(diags, diag.Diagnostic{
					Severity: diag.Error,
					Summary:  fmt.Sprintf("[ERROR] resourceCaepAppInstRead %+v id mismatch %s != %d", apiRes, app_id, d.Id()),
		    })*/
		return diag.Errorf("invalid (mismatched) app_id %s %+v", d.Id(), hm)
	}
	retry := 900
	for app_state == "deploying" && retry > 0 {
		time.Sleep(1 * time.Second)
		retry--
		apiRes, _ = CaepApiGet(m, hm, uri)
		inst = apiRes.Data.(map[string]interface{})
		app_state = inst["state"].(string)
	}
	// get latest host HwResource info
	uri_hwrsc := fmt.Sprintf("http://%s:10288/hwresources", hm.EghostIp)
	apiRes, _ = CaepApiGet(m, hm, uri_hwrsc)
	if apiRes.Data != nil {
		apiRespData := apiRes.Data.(string)
		hm.HwResources = apiRespData
	}
	appVf82mac := ""
	for _, ln := range strings.Split(hm.HwResources, "\n") {
		ln = strings.TrimSpace(ln)
		if strings.Contains(ln, d.Id()) {
			// 0000:07:10.0 70:10:6f:bc:b3:18 in-use  682cebd6-77c7-4532-b78a-8b791cfeb8b0  passthru
			ll := strings.Split(ln, " ")
			if len(ll) > 2 {
				appVf82mac = fmt.Sprintf("%s vf82 %s", ll[0], ll[1])
				break
			}

		}
	}
	appStartTriggered := false
	switch app_state {
	case "ready":
		pt_pci_addrs := d.Get("pci_addr_csv").(string)
		uri_pt := fmt.Sprintf("https://%s:4666/gatekeeper/v1/resources/nodes/%s/apps/%s/nics", hm.EghostIp, hm.EgNodeId, d.Id())
		// curl -X PUT "https://192.168.82.39:4666/gatekeeper/v1/resources/nodes/2502f563-2c20-4954-a724-ffb293d75c19/apps/91ead1f7-28d9-406b-824b-1831412ff8dd/nics" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnYXRla2VlcGVyIiwic3ViIjoiYXBpZ2F0ZXdheSIsImV4cCI6MTY0NzU3NDAwMywiaWF0IjoxNjQ3NDg3NjAzLCJqdGkiOiJnYXRla2VlcGVyIiwidXNlciI6InVzZXIifQ.AKIkZDR4urXsAWRmn8ysPjwOablQ9XdkyMx_r7dH7nI" -d "{\"action\":\"ASSIGN\",\"pci_address\":\"0000:07:10.4\",\"ip\":\"192.168.82.20\",\"method\":\"passthru\"}"
		log.Printf("[DEBUG] resourceCaepAppInstRead %s %s", pt_pci_addrs, uri_pt)
		if pt_pci_addrs == "pt-net82" && appVf82mac == "" {
			for _, ln := range strings.Split(hm.HwResources, "\n") {
				ln = strings.TrimSpace(ln)
				log.Printf("[DEBUG] resourceCaepAppInstRead pt-net82 %s", ln)
				if strings.HasSuffix(ln, " free") {
					pt_pci_addrs = strings.Split(ln, " ")[0]
					d.Set("pci_addr_csv", ln)
					break
				}
			}
		}
		for _, pa := range strings.Split(pt_pci_addrs, ",") {
			pt := map[string]string{"action": "ASSIGN", "method": "passthru",
				"pci_address": strings.TrimSpace(pa), "ip": "192.168.82.20"}
			caepRes, _ := CaepApiPut(m, hm, uri_pt, pt)
			log.Printf("[DEBUG] resourceCaepAppInstRead %+v resp of uri %s %+v", caepRes, uri_pt, pt)
			time.Sleep(1 * time.Second)
		}
		switch app_act {
		case "auto-start", "start":
			pd := map[string]string{"action": "start"}
			caepRes, _ := CaepApiPatch(m, hm, uri, pd)
			log.Printf("[DEBUG] resourceCaepAppInstRead PATCH %s resp %+v", uri, caepRes)
			appStartTriggered = true
		}
	case "running", "stopped":
		switch app_act {
		case "restart", "stop":
			pd := map[string]string{"action": app_act}
			caepRes, _ := CaepApiPatch(m, hm, uri, pd)
			log.Printf("[DEBUG] resourceCaepAppInstRead PATCH %s resp %+v", uri, caepRes)
		}
	case "error":
		switch app_act {
		case "start":
			pd := map[string]string{"action": "start"}
			caepRes, _ := CaepApiPatch(m, hm, uri, pd)
			log.Printf("[DEBUG] resourceCaepAppInstRead PATCH %s resp %+v", uri, caepRes)
			appStartTriggered = true
		}
	case "deploying": // fatal error, should never happened
	}

	/*var retTmp0 appExtraSt
		retTmp0.Flavor = inst["flavor"].(string)
		retTmp0.AppType = inst["app_type"].(string)
	    retTmp0.State = inst["state"].(string)*/

	apiRes, _ = CaepApiGet(m, hm, uri)
	inst = apiRes.Data.(map[string]interface{})
	/*
		d.Set("app_name", inst["app_name"].(string))
		//appConfig.Flavor = inst["flavor"].(string)
		//d.Set("config", appConfig)
		//d.Set("config", inst["flavor"].(string))
		d.Set("status", inst["state"].(string))

		ipConfigs := inst["ip_config"].([]interface{})
		if len(ipConfigs) > 0 {
			ipConfig0 := ipConfigs[0].(map[string]interface{})
			appConfig := fmt.Sprintf("%s\n%s", inst["flavor"].(string), ipConfig0["port_vnic"].(string))
			d.Set("config", appConfig)
			retTmp0.AppManagementIp = fmt.Sprintf("%s", ipConfig0["port_vnic"].(string))
	}*/

	eai := CaepAppInstExt{AppType: inst["app_type"].(string),
		State:  inst["state"].(string),
		Flavor: inst["flavor"].(string),
	}
	ipConfigs := inst["ip_config"].([]interface{})
	if len(ipConfigs) > 0 {
		ipConfig0 := ipConfigs[0].(map[string]interface{})
		eai.AppManagementIp = fmt.Sprintf("%s", ipConfig0["port_vnic"].(string))
	}
	if appVf82mac != "" {
		eai.AppVnics = fmt.Sprintf("%s", appVf82mac)
	}
	uri_appOvs := fmt.Sprintf("http://%s:10288/apps/%s/ovsports", hm.EghostIp, d.Id())
	apiRes1, _ := CaepApiGet(m, hm, uri_appOvs)
	log.Printf("[DEBUG] resourceCaepAppInstRead 10288 ovsports %+v", apiRes1)
	retAppOvsPorts := apiRes1.Data.([]interface{})
	// [int  |192.168.33.133 |00:fb:83:37:b4:df oam  |192.168.44.87  |00:71:9c:82:2f:fb xhaul|192.168.55.156 |00:f1:ad:2c:de:07]
	for _, ovsp := range retAppOvsPorts {
		ll := strings.Split(ovsp.(string), "|")
		eai.AppVnics = fmt.Sprintf("%s\novs %s %s", eai.AppVnics, ll[0], ll[2])
	}

	retAppExt := make([]map[string]interface{}, 0)
	byts, _ := json.Marshal([]CaepAppInstExt{eai})
	json.Unmarshal(byts, &retAppExt)

	d.Set("app_extra", retAppExt)

	if !appStartTriggered {
		return
	}
	retry = 300
	for app_state != "running" && retry > 0 {
		time.Sleep(1 * time.Second)
		retry--
		apiRes, _ = CaepApiGet(m, hm, uri)
		inst = apiRes.Data.(map[string]interface{})
		ipConfigs := inst["ip_config"].([]interface{})
		if len(ipConfigs) > 0 {
			ipConfig0 := ipConfigs[0].(map[string]interface{})
			//appConfig := fmt.Sprintf("%s\n%s", d.Get("config"), ipConfig0["port_vnic"].(string))
			//d.Set("config", appConfig)
			ipConfig0_vnic := ipConfig0["port_vnic"].(string) //ex: "xhaul:192.168.55.166"
			if strings.Contains(ipConfig0_vnic, "192.168.122") {
				log.Printf("%s", ipConfig0_vnic)
				uri = fmt.Sprintf("http://%s:10282/eaa/services/%s/enable", hm.EghostIp, d.Id())
				pd := map[string]string{}
				caepRes, _ := CaepApiPost(m, hm, uri, pd)
				log.Printf("[DEBUG] resourceCaepAppInstRead %+v resp of uri %s", caepRes, uri)
				break
			}
		}
	}
	return diags
}

func resourceCaepAppInstUpdate(ctx context.Context, d *schema.ResourceData, meta interface{}) (diags diag.Diagnostics) {
	// use the meta value to retrieve your client from the provider configure method
	// client := meta.(*apiClient)
	m := meta.(apiClient)
	workerIp := d.Get("worker_ip").(string)
	hm, ok := m.AppRunHostMap[workerIp]
	if !ok {
		return diag.Errorf("invalid worker_ip %s %v", workerIp, hm)
	}
	//m.ApiToken = hm.ApiToken
	uri := fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/nodes/%s/apps/%s", hm.EghostIp, hm.EgNodeId, d.Id())

	app_act := d.Get("action").(string)
	switch app_act {
	case "start", "stop", "restart":
		pd := map[string]string{"action": app_act}
		caepRes, _ := CaepApiPatch(m, hm, uri, pd)
		log.Printf("[DEBUG] resourceCaepAppInstUpdate PATCH %s resp %+v", uri, caepRes)
	}

	return diags
}

func resourceCaepAppInstDelete(ctx context.Context, d *schema.ResourceData, meta interface{}) (diags diag.Diagnostics) {
	// use the meta value to retrieve your client from the provider configure method
	// client := meta.(*apiClient)
	m := meta.(apiClient)
	workerIp := d.Get("worker_ip").(string)
	hm, ok := m.AppRunHostMap[workerIp]
	if !ok {
		return diag.Errorf("invalid worker_ip %s %v", workerIp, hm)
	}
	//m.ApiToken = hm.ApiToken
	uri := fmt.Sprintf("https://%s:4666/gatekeeper/v1/edgeapps/nodes/%s/apps/%s", hm.EghostIp, hm.EgNodeId, d.Id())
	log.Printf("[DEBUG] resourceCaepAppInstDelete %s ", uri)
	apiRes, _ := CaepApiDel(m, hm, uri)
	log.Printf("[DEBUG] resourceCaepAppInstDelete resp %+v ", apiRes)

	return
}
