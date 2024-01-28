package baidu

import (
	"one-api/relay/channel/openai"
	"time"
)

type ChatResponse struct {
	Id               string       `json:"id"`
	Object           string       `json:"object"`
	Created          int64        `json:"created"`
	Result           string       `json:"result"`
	IsTruncated      bool         `json:"is_truncated"`
	NeedClearHistory bool         `json:"need_clear_history"`
	Usage            openai.Usage `json:"usage"`
	BaiduError
}

type ChatStreamResponse struct {
	ChatResponse
	SentenceId int  `json:"sentence_id"`
	IsEnd      bool `json:"is_end"`
}

type EmbeddingRequest struct {
	Input []string `json:"input"`
}

type EmbeddingData struct {
	Object    string    `json:"object"`
	Embedding []float64 `json:"embedding"`
	Index     int       `json:"index"`
}

type EmbeddingResponse struct {
	Id      string          `json:"id"`
	Object  string          `json:"object"`
	Created int64           `json:"created"`
	Data    []EmbeddingData `json:"data"`
	Usage   openai.Usage    `json:"usage"`
	BaiduError
}

type AccessToken struct {
	AccessToken      string    `json:"access_token"`
	Error            string    `json:"error,omitempty"`
	ErrorDescription string    `json:"error_description,omitempty"`
	ExpiresIn        int64     `json:"expires_in,omitempty"`
	ExpiresAt        time.Time `json:"-"`
}
