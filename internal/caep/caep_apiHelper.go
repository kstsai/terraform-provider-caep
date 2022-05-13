package caep

import (
	"bytes"
	//"context"
	//"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/hashicorp/terraform-plugin-sdk/v2/diag"
	//"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
)

type CaepApiRes struct {
	ErrCode int    `json:"err_code"`
	Message string `json:"message"`
	//Data    []map[string]interface{} `json:"data,omitempty"`
	Data interface{} `json:"data,omitempty"`
}

func CaepApiGet(m apiClient, hm caepHostInfo, uri string) (apiRes CaepApiRes, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", uri, nil)
	req.Header.Set("Accept", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", hm.ApiToken))
	respGet, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer respGet.Body.Close()
	err = json.NewDecoder(respGet.Body).Decode(&apiRes)
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	return
}

func CaepApiPost(m apiClient, hm caepHostInfo, uri string, pd map[string]string) (apiRes CaepApiRes, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	reqBody, err := json.Marshal(pd)
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}

	req, err := http.NewRequest("POST",
		uri,
		bytes.NewBuffer(reqBody))
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	req.Header.Set("Content-Type", "application/json;charset=UTF-8")
	req.Header.Set("Accept", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", hm.ApiToken))
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer resp.Body.Close()
	err = json.NewDecoder(resp.Body).Decode(&apiRes)

	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	return
}

func CaepApiPatch(m apiClient, hm caepHostInfo, uri string, pd map[string]string) (apiRes CaepApiRes, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	reqBody, err := json.Marshal(pd)
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}

	req, err := http.NewRequest("PATCH",
		uri,
		bytes.NewBuffer(reqBody))
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	req.Header.Set("Content-Type", "application/json;charset=UTF-8")
	req.Header.Set("Accept", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", hm.ApiToken))
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer resp.Body.Close()
	err = json.NewDecoder(resp.Body).Decode(&apiRes)

	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	return
}

func CaepApiPut(m apiClient, hm caepHostInfo, uri string, pd map[string]string) (apiRes CaepApiRes, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	reqBody, err := json.Marshal(pd)
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}

	req, err := http.NewRequest("PUT",
		uri,
		bytes.NewBuffer(reqBody))
	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	req.Header.Set("Content-Type", "application/json;charset=UTF-8")
	req.Header.Set("Accept", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", hm.ApiToken))
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer resp.Body.Close()
	err = json.NewDecoder(resp.Body).Decode(&apiRes)

	if err != nil {
		log.Printf("[DEBUG] %v", err)
		return
	}
	return
}

func CaepApiDel(m apiClient, hm caepHostInfo, uri string) (apiRes CaepApiRes, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("DELETE", uri, nil)
	req.Header.Set("Accept", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", hm.ApiToken))
	respGet, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer respGet.Body.Close()
	err = json.NewDecoder(respGet.Body).Decode(&apiRes)

	respBody, err := ioutil.ReadAll(respGet.Body)
	err = json.Unmarshal(respBody, apiRes)
	if err != nil {
		log.Printf("[ERROR] %v %s", err, string(respBody))
		return apiRes, diag.Errorf("API response unmarshal(%s) got error %v", string(respBody), err)
	}
	return
}

type apiResComputeUsable struct {
	MemUsedMb         int     `json:"memUsedMb"`
	HomeDiskTotalGb   int     `json:"homeDiskTotalGb"`
	SwapTotalMb       int     `json:"swapTotalMb"`
	SwapFreeMb        int     `json:"swapFreeMb"`
	SwapUsedMb        int     `json:"swapUsedMb"`
	VcpuFree          int     `json:"vcpuFree"`
	VMAppTotalQuotaGb int     `json:"vmAppTotalQuotaGb"`
	VcpuUsed          int     `json:"vcpuUsed"`
	VcpuTotal         int     `json:"vcpuTotal"`
	MemTotalMb        int     `json:"memTotalMb"`
	HugepageUsedGb    int     `json:"hugepageUsedGb"`
	HomeDiskUsedGb    int     `json:"homeDiskUsedGb"`
	RootDiskTotalGb   float64 `json:"rootDiskTotalGb"`
	BackDiskInfo      string  `json:"backDiskInfo,omitempty"`
	RootDiskUsedGb    float64 `json:"rootDiskUsedGb"`
	Hostname          string  `json:"hostname"`
	HugepageFreeGb    int     `json:"hugepageFreeGb"`
	MemFreeMb         int     `json:"memFreeMb"`
	HugepageTotalGb   int     `json:"hugepageTotalGb"`
}

func CaepApiComputeUsable(m apiClient, uri string) (apiRes apiResComputeUsable, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", uri, nil)
	req.Header.Set("Accept", "application/json")
	respGet, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer respGet.Body.Close()
	err = json.NewDecoder(respGet.Body).Decode(&apiRes)
	return
}

type apiResEaaServices struct {
	Services []struct {
		Urn struct {
			ID        string `json:"id"`
			Namespace string `json:"namespace"`
		} `json:"urn"`
		Description   string `json:"description"`
		EndpointURI   string `json:"endpoint_uri"`
		Notifications []struct {
			Name    string `json:"name"`
			Version string `json:"version"`
		} `json:"notifications"`
	} `json:"services"`
}

func CaepApiEaaServices(m apiClient, uri string) (apiRes apiResEaaServices, diags diag.Diagnostics) {

	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", uri, nil)
	req.Header.Set("Accept", "application/json")
	respGet, err := client.Do(req)
	if err != nil {
		log.Printf("[ERROR] %v", err)
		return apiRes, diag.Errorf("API to %v got error %v", req, err)
	}
	defer respGet.Body.Close()
	err = json.NewDecoder(respGet.Body).Decode(&apiRes)
	return
}
