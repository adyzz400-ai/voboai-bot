package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os/exec"
)

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	School   string `json:"school"`
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(
			w,
			"method not allowed",
			http.StatusMethodNotAllowed,
		)
		return
	}

	body, err := io.ReadAll(r.Body)

	if err != nil {
		http.Error(
			w,
			"failed to read request",
			http.StatusBadRequest,
		)
		return
	}

	var request LoginRequest

	if err := json.Unmarshal(body, &request); err != nil {
		http.Error(
			w,
			"invalid JSON",
			http.StatusBadRequest,
		)
		return
	}

	if request.Username == "" ||
		request.Password == "" ||
		request.School == "" {

		http.Error(
			w,
			"missing login information",
			http.StatusBadRequest,
		)

		return
	}

	payload, err := json.Marshal(request)

	if err != nil {
		http.Error(
			w,
			"failed to encode request",
			http.StatusInternalServerError,
		)

		return
	}

	cmd := exec.Command(
		"node",
		"sparx/worker.js",
	)

	cmd.Stdin = bytes.NewReader(payload)

	output, err := cmd.CombinedOutput()

	if err != nil {
		http.Error(
			w,
			string(output),
			http.StatusBadGateway,
		)

		return
	}

	w.Header().Set(
		"Content-Type",
		"application/json",
	)

	_, _ = w.Write(output)
}

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc(
		"/health",
		func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)

			_, _ = w.Write(
				[]byte("VoboAi Sparx worker is running"),
			)
		},
	)

	mux.HandleFunc(
		"/login",
		loginHandler,
	)

	log.Println(
		"VoboAi Sparx Go worker listening on :8787",
	)

	log.Fatal(
		http.ListenAndServe(
			":8787",
			mux,
		),
	)
}
