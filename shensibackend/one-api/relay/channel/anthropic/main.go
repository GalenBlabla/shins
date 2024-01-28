package anthropic

import (
	"bufio"
	"encoding/json"
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	"one-api/common"
	"one-api/relay/channel/openai"
	"strings"
)

func stopReasonClaude2OpenAI(reason string) string {
	switch reason {
	case "stop_sequence":
		return "stop"
	case "max_tokens":
		return "length"
	default:
		return reason
	}
}

func ConvertRequest(textRequest openai.GeneralOpenAIRequest) *Request {
	claudeRequest := Request{
		Model:             textRequest.Model,
		Prompt:            "",
		MaxTokensToSample: textRequest.MaxTokens,
		StopSequences:     nil,
		Temperature:       textRequest.Temperature,
		TopP:              textRequest.TopP,
		Stream:            textRequest.Stream,
	}
	if claudeRequest.MaxTokensToSample == 0 {
		claudeRequest.MaxTokensToSample = 1000000
	}
	prompt := ""
	for _, message := range textRequest.Messages {
		if message.Role == "user" {
			prompt += fmt.Sprintf("\n\nHuman: %s", message.Content)
		} else if message.Role == "assistant" {
			prompt += fmt.Sprintf("\n\nAssistant: %s", message.Content)
		} else if message.Role == "system" {
			if prompt == "" {
				prompt = message.StringContent()
			}
		}
	}
	prompt += "\n\nAssistant:"
	claudeRequest.Prompt = prompt
	return &claudeRequest
}

func streamResponseClaude2OpenAI(claudeResponse *Response) *openai.ChatCompletionsStreamResponse {
	var choice openai.ChatCompletionsStreamResponseChoice
	choice.Delta.Content = claudeResponse.Completion
	finishReason := stopReasonClaude2OpenAI(claudeResponse.StopReason)
	if finishReason != "null" {
		choice.FinishReason = &finishReason
	}
	var response openai.ChatCompletionsStreamResponse
	response.Object = "chat.completion.chunk"
	response.Model = claudeResponse.Model
	response.Choices = []openai.ChatCompletionsStreamResponseChoice{choice}
	return &response
}

func responseClaude2OpenAI(claudeResponse *Response) *openai.TextResponse {
	choice := openai.TextResponseChoice{
		Index: 0,
		Message: openai.Message{
			Role:    "assistant",
			Content: strings.TrimPrefix(claudeResponse.Completion, " "),
			Name:    nil,
		},
		FinishReason: stopReasonClaude2OpenAI(claudeResponse.StopReason),
	}
	fullTextResponse := openai.TextResponse{
		Id:      fmt.Sprintf("chatcmpl-%s", common.GetUUID()),
		Object:  "chat.completion",
		Created: common.GetTimestamp(),
		Choices: []openai.TextResponseChoice{choice},
	}
	return &fullTextResponse
}

func StreamHandler(c *gin.Context, resp *http.Response) (*openai.ErrorWithStatusCode, string) {
	responseText := ""
	responseId := fmt.Sprintf("chatcmpl-%s", common.GetUUID())
	createdTime := common.GetTimestamp()
	scanner := bufio.NewScanner(resp.Body)
	scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
		if atEOF && len(data) == 0 {
			return 0, nil, nil
		}
		if i := strings.Index(string(data), "\r\n\r\n"); i >= 0 {
			return i + 4, data[0:i], nil
		}
		if atEOF {
			return len(data), data, nil
		}
		return 0, nil, nil
	})
	dataChan := make(chan string)
	stopChan := make(chan bool)
	go func() {
		for scanner.Scan() {
			data := scanner.Text()
			if !strings.HasPrefix(data, "event: completion") {
				continue
			}
			data = strings.TrimPrefix(data, "event: completion\r\ndata: ")
			dataChan <- data
		}
		stopChan <- true
	}()
	common.SetEventStreamHeaders(c)
	c.Stream(func(w io.Writer) bool {
		select {
		case data := <-dataChan:
			// some implementations may add \r at the end of data
			data = strings.TrimSuffix(data, "\r")
			var claudeResponse Response
			err := json.Unmarshal([]byte(data), &claudeResponse)
			if err != nil {
				common.SysError("error unmarshalling stream response: " + err.Error())
				return true
			}
			responseText += claudeResponse.Completion
			response := streamResponseClaude2OpenAI(&claudeResponse)
			response.Id = responseId
			response.Created = createdTime
			jsonStr, err := json.Marshal(response)
			if err != nil {
				common.SysError("error marshalling stream response: " + err.Error())
				return true
			}
			c.Render(-1, common.CustomEvent{Data: "data: " + string(jsonStr)})
			return true
		case <-stopChan:
			c.Render(-1, common.CustomEvent{Data: "data: [DONE]"})
			return false
		}
	})
	err := resp.Body.Close()
	if err != nil {
		return openai.ErrorWrapper(err, "close_response_body_failed", http.StatusInternalServerError), ""
	}
	return nil, responseText
}

func Handler(c *gin.Context, resp *http.Response, promptTokens int, model string) (*openai.ErrorWithStatusCode, *openai.Usage) {
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return openai.ErrorWrapper(err, "read_response_body_failed", http.StatusInternalServerError), nil
	}
	err = resp.Body.Close()
	if err != nil {
		return openai.ErrorWrapper(err, "close_response_body_failed", http.StatusInternalServerError), nil
	}
	var claudeResponse Response
	err = json.Unmarshal(responseBody, &claudeResponse)
	if err != nil {
		return openai.ErrorWrapper(err, "unmarshal_response_body_failed", http.StatusInternalServerError), nil
	}
	if claudeResponse.Error.Type != "" {
		return &openai.ErrorWithStatusCode{
			Error: openai.Error{
				Message: claudeResponse.Error.Message,
				Type:    claudeResponse.Error.Type,
				Param:   "",
				Code:    claudeResponse.Error.Type,
			},
			StatusCode: resp.StatusCode,
		}, nil
	}
	fullTextResponse := responseClaude2OpenAI(&claudeResponse)
	fullTextResponse.Model = model
	completionTokens := openai.CountTokenText(claudeResponse.Completion, model)
	usage := openai.Usage{
		PromptTokens:     promptTokens,
		CompletionTokens: completionTokens,
		TotalTokens:      promptTokens + completionTokens,
	}
	fullTextResponse.Usage = usage
	jsonResponse, err := json.Marshal(fullTextResponse)
	if err != nil {
		return openai.ErrorWrapper(err, "marshal_response_body_failed", http.StatusInternalServerError), nil
	}
	c.Writer.Header().Set("Content-Type", "application/json")
	c.Writer.WriteHeader(resp.StatusCode)
	_, err = c.Writer.Write(jsonResponse)
	return nil, &usage
}
