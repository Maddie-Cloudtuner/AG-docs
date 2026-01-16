{{/*
Expand the name of the chart.
*/}}
{{- define "kubecost-integration.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "kubecost-integration.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kubecost-integration.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kubecost-integration.labels" -}}
helm.sh/chart: {{ include "kubecost-integration.chart" . }}
{{ include "kubecost-integration.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: kubecost-integration
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kubecost-integration.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kubecost-integration.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "kubecost-integration.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "kubecost-integration.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create CloudTuner storage configuration
*/}}
{{- define "kubecost-integration.storageConfig" -}}
influxdb:
  url: {{ .Values.kubecost.cloudtuner.storage.influxdb }}
clickhouse:
  url: {{ .Values.kubecost.cloudtuner.storage.clickhouse }}
{{- end }}

{{/*
Create Kubecost endpoint configuration
*/}}
{{- define "kubecost-integration.kubecostConfig" -}}
endpoint: {{ .Values.extractor.config.kubecostEndpoint }}
timeout: {{ .Values.extractor.config.timeout }}
retries: {{ .Values.extractor.config.retries }}
batchSize: {{ .Values.extractor.config.batchSize }}
{{- end }}