package caep

import (
	"bytes"
	"context"
	"crypto/tls"

	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/hashicorp/terraform-plugin-sdk/v2/diag"
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
)

const (
	EGNODEHOST = "caep_edgehost"
	EGSVCINST  = "caep_edgesvc"
)

//func Provider() *schema.Provider {
//	return &schema.Provider{
func New(version string) func() *schema.Provider {
	return func() *schema.Provider {

		eghostSchema := map[string]*schema.Schema{
			/*
						"username": &schema.Schema{
							Type:        schema.TypeString,
							Optional:    true,
							DefaultFunc: schema.EnvDefaultFunc("CAEP_USERNAME", nil),
						},
						"password": &schema.Schema{
							Type:        schema.TypeString,
							Optional:    true,
							Sensitive:   true,
							DefaultFunc: schema.EnvDefaultFunc("CAEP_PASSWORD", nil),
						},
						"aio_ip_csv": &schema.Schema{
							Type:        schema.TypeString,
							Optional:    true,
							Sensitive:   true,
							DefaultFunc: schema.EnvDefaultFunc("CAEP_HOST", nil),
						},
						"aio_name_csv": &schema.Schema{
							Type:      schema.TypeString,
							Optional:  true,
							Sensitive: true,
			        },*/
			"aio_workers": &schema.Schema{
				Type:     schema.TypeList,
				Required: true,
				Elem: &schema.Resource{
					Schema: map[string]*schema.Schema{
						"worker": &schema.Schema{
							Type:     schema.TypeList,
							MaxItems: 255,
							Required: true,
							Elem: &schema.Resource{
								Schema: map[string]*schema.Schema{
									"aio_ip": &schema.Schema{
										Type:     schema.TypeString,
										Required: true,
									},
									"aio_dns": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"description": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
									"aio_user": &schema.Schema{
										Type:        schema.TypeString,
										Optional:    true,
										DefaultFunc: schema.EnvDefaultFunc("AIO_USER", "user"),
									},
									"aio_pass": &schema.Schema{
										Type:        schema.TypeString,
										Optional:    true,
										DefaultFunc: schema.EnvDefaultFunc("AIO_PASS", "123456"),
									},
									"aio_extra": &schema.Schema{
										Type:     schema.TypeString,
										Computed: true,
									},
								},
							},
						},
					},
				},
			},
		}

		p := &schema.Provider{
			/*
				Schema: map[string]*schema.Schema{

					"username": &schema.Schema{
						Type:        schema.TypeString,
						Optional:    true,
						DefaultFunc: schema.EnvDefaultFunc("CAEP_USERNAME", nil),
					},
					"password": &schema.Schema{
						Type:        schema.TypeString,
						Optional:    true,
						Sensitive:   true,
						DefaultFunc: schema.EnvDefaultFunc("CAEP_PASSWORD", nil),
					},
					"host": &schema.Schema{
						Type:        schema.TypeString,
						Optional:    true,
						Sensitive:   true,
						DefaultFunc: schema.EnvDefaultFunc("CAEP_HOST", nil),
					},
				},*/

			Schema: eghostSchema,
			ResourcesMap: map[string]*schema.Resource{
				//"caep_resource": resourceCaep(),
				//"caep_apptempl": resourceCaepAppTempl(),
				EGSVCINST: resourceCaepAppInst(),
			},
			DataSourcesMap: map[string]*schema.Resource{
				EGNODEHOST: dataSourceCaep(),
			},
		}
		p.ConfigureContextFunc = configure(version, p)

		return p
	}
}

type caepAppTemplate struct {
	AppType      string
	TemplateName string
	TemplateId   string
	Flavor       string
}
type caepHostInfo struct {
	EghostIp     string
	EghostDns    string
	EgNodeId     string
	ApiToken     string
	HwResources  string
	AppTemplates []caepAppTemplate
}

type apiClient struct {
	// Add whatever fields, client or connection info, etc. here
	// you would need to setup to communicate with the upstream
	// API.
	//Eghost        string
	//EgNodeId      string
	AppRunHostMap map[string]caepHostInfo
	//ApiToken      string
	AppTemplates []caepAppTemplate
	BackupAioIp  string
}

//func getApiTokenFromCaepEdge(meta *apiClient, diags diag.Diagnostics) (ret string) {
func getApiTokenFromCaepEdge(hostIp string, username string, password string, diags diag.Diagnostics) (ret string) {

	http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	client := &http.Client{Timeout: 10 * time.Second}

	// Warning or errors can be collected in a slice type
	type CaepAuthReq struct {
		Name     string `json:"name"`
		Password string `json:"password"`
	}
	type CaepAuthRes struct {
		ErrCode int    `json:"err_code"`
		Message string `json:"message"`
		Data    struct {
			Token string `json:"token"`
			Role  string `json:"role"`
		} `json:"data"`
	}
	authReqBody := CaepAuthReq{Name: username, Password: password}

	//    values := map[string]string{"name": "John Doe", "occupation": "gardener"}

	payload, err := json.Marshal(&authReqBody)
	req, _ := http.NewRequest("POST",
		"https://"+hostIp+":4666/gatekeeper/v1/auth",
		bytes.NewBuffer(payload))
	req.Header.Set("Content-Type", "application/json")
	respPost, err := client.Do(req)
	if err != nil {
		diags = append(diags, diag.Diagnostic{
			Severity: diag.Error,
			Summary:  fmt.Sprintf("%v", err),
			Detail:   "test debug message print, detail field",
		})
		return
	}
	defer respPost.Body.Close()
	respBody, err := ioutil.ReadAll(respPost.Body)
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	log.Printf("[DEBUG] %v", string(respBody))
	var caepAuthRes CaepAuthRes
	err = json.Unmarshal(respBody, &caepAuthRes)
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	//meta.ApiToken = caepAuthRes.Data.Token
	return caepAuthRes.Data.Token
}

func configure(version string, p *schema.Provider) func(context.Context, *schema.ResourceData) (interface{}, diag.Diagnostics) {
	return func(ctx context.Context, d *schema.ResourceData) (interface{}, diag.Diagnostics) {

		var meta apiClient
		var diags diag.Diagnostics

		// Setup a User-Agent for your API client (replace the provider name for yours):
		// userAgent := p.UserAgent("terraform-provider-scaffolding", version)
		// TODO: myClient.UserAgent = userAgent
		//meta.Username = d.Get("username").(string)
		//meta.Password = d.Get("password").(string)

		workers := d.Get("aio_workers").([]interface{})
		w := workers[0].(map[string]interface{})
		w2 := w["worker"]
		log.Printf("[DEBUG] provider tf block worker %+v", w2)
		meta.AppRunHostMap = make(map[string]caepHostInfo)
		for idx, w3 := range w2.([]interface{}) {
			wit := w3.(map[string]interface{})
			log.Printf("[DEBUG] provider tf block work%d %v %s", idx, w3, wit["aio_ip"])

			hostIp := wit["aio_ip"].(string)
			user := wit["aio_user"].(string)
			pass := wit["aio_pass"].(string)
			apiToken := getApiTokenFromCaepEdge(hostIp, user, pass, diags)
			if apiToken == "" {
				continue
			}
			hostDns := wit["aio_dns"].(string)
			if hostDns == "" {
				dotSplitted := strings.Split(hostIp, ".")
				hostDns = fmt.Sprintf("worker_%s", dotSplitted[len(dotSplitted)-1])
			}

			var hm caepHostInfo
			hm.EghostIp = hostIp
			hm.EghostDns = hostDns
			hm.ApiToken = apiToken

			uri := fmt.Sprintf("http://%s:10286/health", hostIp)
			egHostHealth, _ := CaepApiGet(meta, hm, uri)
			regExpression := fmt.Sprintf("=[0-9a-z\\-]{36},online=%s", hostIp)
			re := regexp.MustCompile(regExpression)
			matches := re.FindStringSubmatch(egHostHealth.Message)
			if matches != nil {
				node_id := matches[0][1:37]
				//uri := fmt.Sprintf("http://%s:10288/compute/usable", hostIp)
				//apiRes, _ := CaepApiComputeUsable(meta, uri)
				uri := fmt.Sprintf("http://%s:10288/hwresources", hostIp)
				//meta.ApiToken = apiToken
				apiRes, _ := CaepApiGet(meta, hm, uri)
				if apiRes.Data != nil {
					apiRespData := apiRes.Data.(string)
					//log.Printf("[DEBUG] provider %s resp %s", uri, apiRespData)
					if strings.Contains(apiRespData, "APPBACKUP") {
						//log.Printf("[DEBUG] provider %s set meta.BackAioIp = %s", uri, hostIp)
						meta.BackupAioIp = hostIp
					}
					hm.HwResources = apiRespData
				}
				hm.EgNodeId = node_id
				meta.AppRunHostMap[hostIp] = hm
			}
		}
		return meta, diags
	}
}
