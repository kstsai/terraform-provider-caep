package main

import (
	"encoding/json"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
	"reflect"
	//"strings"
	"testing"
)

type outputWorkerBrief struct {
	AioShowAppInstances   bool   `json:"aio_show_app_instances"`
	AioShowAppTemplates   bool   `json:"aio_show_app_templates"`
	AioShowDeployableApps bool   `json:"aio_show_deployable_apps"`
	BackableHost          string `json:"backable_host"`
	CaepEdgehost          []struct {
		AioBackupVol  string `json:"aio_backup_vol"`
		AioBrief      string `json:"aio_brief"`
		AioIP         string `json:"aio_ip"`
		AppDeployable []struct {
			AppName string `json:"app_name"`
			AppType string `json:"app_type"`
			Flavor  string `json:"flavor"`
		} `json:"app_deployable"`
		AppInstances []interface{} `json:"app_instances"`
		AppTemplates []struct {
			AppName string `json:"app_name"`
			AppType string `json:"app_type"`
			Flavor  string `json:"flavor"`
		} `json:"app_templates"`
	} `json:"caep_edgehost"`
	FilterPattern string `json:"filter_pattern"`
	ID            string `json:"id"`
	WorkerIP      string `json:"worker_ip"`
}

func TestTerraformHelloWorldExample(t *testing.T) {
	// retryable errors in terraform testing.
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "./examples",
	})

	defer terraform.Destroy(t, terraformOptions)

	terraform.InitAndApply(t, terraformOptions)

	output := terraform.OutputJson(t, terraformOptions, "outWorkerBrief1")
	t.Logf("%+v", output)
	//out := output.(map[string]interface{})
	var out outputWorkerBrief
	err := json.Unmarshal([]byte(output), &out)

	t.Logf("%v\n %+v\n %v %v", err, out, reflect.TypeOf(out), reflect.TypeOf(output))

	assert.Less(t, 0, len(out.CaepEdgehost))
	if out.AioShowDeployableApps {
		assert.NotEqual(t, 0, len(out.CaepEdgehost[0].AppDeployable))
	}
	if !out.AioShowAppInstances {
		assert.Equal(t, 0, len(out.CaepEdgehost[0].AppInstances))
	}
	assert.Equal(t, 1, 1)
}
