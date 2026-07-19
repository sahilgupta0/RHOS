import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { consultationApi, patientsApi } from "../../api";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { cn } from "../../lib/utils";
import {
  Send,
  Mic,
  MicOff,
  ImagePlus,
  Bot,
  User,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Shield,
  ClipboardCheck,
  Trash2,
  RotateCcw,
} from "lucide-react";
import type { ChatMessage, Consultation } from "../../types";
import LoadingSpinner from "../../components/common/LoadingSpinner";

const SYSTEM_NOTICE: ChatMessage = {
  id: "system-1",
  role: "system",
  content: "⚠️ RHOS is a Clinical Decision Support System. AI outputs are advisory only — all medical decisions are made by the treating physician.",
  timestamp: new Date(),
};

export default function ConsultationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [activeConsultation, setActiveConsultation] = useState<Consultation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([SYSTEM_NOTICE]);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedPatientId, setSelectedPatientId] = useState("");
  const [uploadingImage, setUploadingImage] = useState(false);
  const [isClearingChat, setIsClearingChat] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [readyToSubmit, setReadyToSubmit] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pipelineStatus, setPipelineStatus] = useState<Record<string, string>>({
    conversation: "pending",
    history: "pending",
    triage: "pending",
    medicine: "pending",
    doctor: "pending",
    followup: "pending",
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch patients for doctor/nurse selection
  const { data: patients } = useQuery({
    queryKey: ["patients"],
    queryFn: () => patientsApi.list({ page_size: 100 }).then((res) => res.patients),
    enabled: user?.role !== "patient",
  });

  // Fetch existing consultation details if ID is in parameters
  const { data: fetchedConsultation, isLoading: loadingConsultation } = useQuery({
    queryKey: ["consultation", id],
    queryFn: () => consultationApi.getById(id!),
    enabled: !!id,
  });

  // Automatically start or load consultation for Patient role
  const { data: patientConsultations, isLoading: loadingPatientConsultation } = useQuery({
    queryKey: ["patientConsultations", user?.patient_id],
    queryFn: () => consultationApi.list({ patient_id: user?.patient_id }),
    enabled: user?.role === "patient" && !id,
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load existing consultation history
  useEffect(() => {
    if (fetchedConsultation) {
      setActiveConsultation(fetchedConsultation);
      const chatMsgs: ChatMessage[] = [SYSTEM_NOTICE];
      
      const history = fetchedConsultation.conversation_history || [];
      history.forEach((h: any, idx: number) => {
        chatMsgs.push({
          id: `msg-${idx}`,
          role: h.role as "patient" | "assistant" | "system",
          content: h.content,
          timestamp: new Date(),
          agentName: h.role === "assistant" ? "AI Agent Pipeline" : undefined,
        });
      });

      if (chatMsgs.length === 1) {
        chatMsgs.push({
          id: "welcome",
          role: "assistant",
          content: `Hello! I'm the RHOS clinical assistant. Please describe the symptoms, and I'll run the multi-agent decision support pipeline.\n\nChief complaint: "${fetchedConsultation.chief_complaint || "Not specified"}"`,
          timestamp: new Date(),
          agentName: "Conversation Agent",
        });
      }

      setMessages(chatMsgs);
    }
  }, [fetchedConsultation]);

  // Handle patient role auto-load/start
  useEffect(() => {
    if (user?.role === "patient" && !id && patientConsultations) {
      if (patientConsultations.length > 0) {
        // Load latest consultation
        const latest = patientConsultations[0];
        navigate(`/consultation/${latest.id}`);
      } else {
        // Start a new one
        startNewConsultation(user.patient_id || "P001", "Routine AI Wellness Check");
      }
    }
  }, [user, patientConsultations, id]);

  const startNewConsultation = async (patientIdStr: string, complaint: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const newCons = await consultationApi.start({
        patient_id: patientIdStr,
        chief_complaint: complaint || "General consultation",
      });
      navigate(`/consultation/${newCons.id}`);
    } catch (err: any) {
      console.error("Failed to start consultation", err);
      setError(err.response?.data?.detail || "Failed to start consultation. Please check backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading || !activeConsultation) return;

    const userMsgText = input.trim();
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "patient",
      content: userMsgText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setError(null);
    // Only conversation agent is active during chat; others stay pending
    setPipelineStatus({
      conversation: "active",
      history: "pending",
      triage: "pending",
      medicine: "pending",
      doctor: "pending",
      followup: "pending",
    });

    try {
      const response = await consultationApi.chat({
        consultation_id: activeConsultation.id,
        message: userMsgText,
      });

      // Only conversation completes; full pipeline runs on Submit
      setPipelineStatus({
        conversation: "completed",
        history: "pending",
        triage: "pending",
        medicine: "pending",
        doctor: "pending",
        followup: "pending",
      });

      // Check if agent thinks we have enough info
      if (response.ready_to_submit) {
        setReadyToSubmit(true);
      }

      const agentMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.agent_response || "No response generated.",
        timestamp: new Date(),
        agentName: "Conversation Agent",
      };

      setMessages((prev) => [...prev, agentMsg]);
      queryClient.invalidateQueries({ queryKey: ["consultation", id] });
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to connect to the backend agent pipeline. Please try again.");
      setPipelineStatus({
        conversation: "pending",
        history: "pending",
        triage: "pending",
        medicine: "pending",
        doctor: "pending",
        followup: "pending",
      });
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "system",
          content: "❌ Failed to connect to the backend agent pipeline. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (!activeConsultation) return;
    setIsClearingChat(true);
    setShowClearConfirm(false);
    setError(null);
    try {
      await consultationApi.clearChat(activeConsultation.id);
      setMessages([SYSTEM_NOTICE, {
        id: "welcome-reset",
        role: "assistant",
        content: `Chat cleared. Describe the symptoms again whenever you're ready.\n\nChief complaint: "${activeConsultation.chief_complaint || "Not specified"}"`,
        timestamp: new Date(),
        agentName: "Conversation Agent",
      }]);
      setReadyToSubmit(false);
      setPipelineStatus({
        conversation: "pending",
        history: "pending",
        triage: "pending",
        medicine: "pending",
        doctor: "pending",
        followup: "pending",
      });
      queryClient.invalidateQueries({ queryKey: ["consultation", id] });
    } catch (err: any) {
      console.error("Failed to clear chat", err);
      setError(err.response?.data?.detail || "Failed to clear chat history.");
    } finally {
      setIsClearingChat(false);
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting || !activeConsultation) return;

    setIsSubmitting(true);
    setReadyToSubmit(false);
    setError(null);

    // Animate each pipeline stage sequentially
    const allStages = ["conversation", "history", "triage", "medicine", "doctor", "followup"];
    let stageIdx = 0;

    const advanceStage = () => {
      setPipelineStatus((prev) => {
        const next = { ...prev };
        if (stageIdx > 0) next[allStages[stageIdx - 1]] = "completed";
        if (stageIdx < allStages.length) next[allStages[stageIdx]] = "active";
        return next;
      });
      stageIdx++;
    };


    try {
      console.log("sending this data : ", activeConsultation.id)
      const response = await consultationApi.submit(activeConsultation.id);


      setMessages((prev) => [
        ...prev,
        {
          id: `submit-${Date.now()}`,
          role: "assistant" as const,
          content: response.agent_response || "Clinical review complete.",
          timestamp: new Date(),
          agentName: "RHOS Clinical Pipeline",
        },
      ]);
      queryClient.invalidateQueries({ queryKey: ["consultation", id] });
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to run the clinical pipeline. Please try again.");
      setPipelineStatus({
        conversation: "completed",
        history: "pending",
        triage: "pending",
        medicine: "pending",
        doctor: "pending",
        followup: "pending",
      });
      setMessages((prev) => [
        ...prev,
        {
          id: `error-submit-${Date.now()}`,
          role: "system" as const,
          content: "❌ Failed to run the clinical pipeline. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !activeConsultation) return;

    setUploadingImage(true);
    setIsLoading(true);
    setError(null);

    try {
      const res = await consultationApi.uploadImage(activeConsultation.id, file);
      
      // Append a local system log in chat
      setMessages((prev) => [
        ...prev,
        {
          id: `sys-img-${Date.now()}`,
          role: "system",
          content: `📷 Medical Image Uploaded (${file.name}). Findings: "${res.findings}"`,
          timestamp: new Date(),
        },
      ]);

      // Automatically send a followup message to trigger agents on the image findings
      setInput(`Please review the uploaded medical image findings: ${res.findings}`);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to upload and analyze image. Please check backend connection.");
    } finally {
      setUploadingImage(false);
      setIsLoading(false);
    }
  };

  const toggleRecording = () => {
    if (!isRecording) {
      if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = "en-IN";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput((prev) => prev + (prev ? " " : "") + transcript);
          setIsRecording(false);
        };

        recognition.onerror = () => setIsRecording(false);
        recognition.onend = () => setIsRecording(false);
        recognition.start();
        setIsRecording(true);
      } else {
        alert("Speech Recognition not supported in this browser.");
      }
    } else {
      setIsRecording(false);
    }
  };

  if (loadingConsultation || loadingPatientConsultation) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  // Doctor/Nurse select patient screen if no active consultation ID is loaded
  if (!id && user?.role !== "patient") {
    return (
      <div className="mx-auto max-w-xl space-y-6 py-10">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Start Clinical Consultation</h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
            Select a patient to begin the AI decision support pipeline
          </p>
        </div>

        {error && (
          <div className="rounded-2xl border border-rose-200 bg-rose-50/50 p-4 text-sm text-rose-700 dark:border-rose-900/30 dark:bg-rose-950/10 dark:text-rose-400 flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-rose-500 hover:text-rose-700 font-bold ml-2">✕</button>
          </div>
        )}

        <div className="rounded-3xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-md space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Select Patient</label>
            <select
              value={selectedPatientId}
              onChange={(e) => setSelectedPatientId(e.target.value)}
              className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            >
              <option value="">-- Choose Patient --</option>
              {patients?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.age} yrs • {p.gender})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => startNewConsultation(selectedPatientId, "General symptoms review")}
            disabled={!selectedPatientId || isLoading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-primary py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl disabled:opacity-50"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Start Consultation"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Main chat area */}
      <div className="flex flex-1 flex-col rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[hsl(var(--border))] px-5 py-3">
          <div>
            <h2 className="text-lg font-semibold">AI Consultation</h2>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">Multi-agent clinical decision support pipeline</p>
          </div>
          <div className="flex items-center gap-2">
            {activeConsultation && (
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full dark:bg-emerald-900/20 dark:text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> ID: {activeConsultation.id}
              </div>
            )}
            {activeConsultation && (
              <button
                onClick={() => setShowClearConfirm(true)}
                disabled={isClearingChat || isLoading || isSubmitting}
                title="Clear chat history and restart"
                className="flex items-center gap-1.5 rounded-xl border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-900/20 px-3 py-1.5 text-xs font-medium text-rose-600 dark:text-rose-400 transition-all hover:bg-rose-100 dark:hover:bg-rose-900/40 disabled:opacity-40"
              >
                {isClearingChat ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RotateCcw className="h-3.5 w-3.5" />}
                Clear Chat
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-thin">
          {error && (
            <div className="rounded-xl border border-rose-200 bg-rose-50/50 p-4 text-xs text-rose-700 dark:border-rose-900/30 dark:bg-rose-950/10 dark:text-rose-400 flex justify-between items-center animate-slide-up">
              <span>{error}</span>
              <button onClick={() => setError(null)} className="text-rose-500 hover:text-rose-700 font-bold ml-2">✕</button>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "flex gap-3 animate-slide-up",
                msg.role === "patient" && "flex-row-reverse"
              )}
            >
              <div className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                msg.role === "patient" ? "bg-blue-100 dark:bg-blue-900/30" :
                msg.role === "system" ? "bg-amber-100 dark:bg-amber-900/30" :
                "bg-gradient-primary text-white"
              )}>
                {msg.role === "patient" ? <User className="h-4 w-4 text-blue-600 dark:text-blue-400" /> :
                 msg.role === "system" ? <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" /> :
                 <Bot className="h-4 w-4" />}
              </div>

              <div className={cn(
                "max-w-[75%] rounded-2xl px-4 py-3",
                msg.role === "patient"
                  ? "bg-gradient-primary text-white rounded-br-md"
                  : msg.role === "system"
                  ? "bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-bl-md"
                  : "bg-[hsl(var(--muted))] rounded-bl-md"
              )}>
                {msg.agentName && (
                  <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider opacity-70">
                    {msg.agentName}
                  </p>
                )}
                <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                <p className={cn(
                  "mt-1.5 text-[10px] opacity-50",
                  msg.role === "patient" ? "text-right" : "text-left"
                )}>
                  {msg.timestamp.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 animate-slide-up">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-primary text-white">
                <Bot className="h-4 w-4 animate-bounce" />
              </div>
              <div className="rounded-2xl rounded-bl-md bg-[hsl(var(--muted))] px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                  RHOS agents running sequential orchestration...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Clear Chat Confirmation Dialog */}
        {showClearConfirm && (
          <div className="absolute inset-0 z-50 flex items-center justify-center rounded-2xl bg-black/40 backdrop-blur-sm">
            <div className="mx-4 w-full max-w-sm rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-xl">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-rose-100 dark:bg-rose-900/30">
                <Trash2 className="h-6 w-6 text-rose-600 dark:text-rose-400" />
              </div>
              <h3 className="mb-1 text-base font-semibold">Clear this chat?</h3>
              <p className="mb-5 text-sm text-[hsl(var(--muted-foreground))]">All conversation history will be deleted and you'll start fresh. This cannot be undone.</p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowClearConfirm(false)}
                  className="flex-1 rounded-xl border border-[hsl(var(--border))] py-2 text-sm font-medium transition-colors hover:bg-[hsl(var(--accent))]"
                >
                  Cancel
                </button>
                <button
                  onClick={handleClearChat}
                  className="flex-1 rounded-xl bg-rose-600 py-2 text-sm font-semibold text-white transition-colors hover:bg-rose-700"
                >
                  Yes, Clear
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Ready-to-submit hint banner */}
        {readyToSubmit && activeConsultation && !isSubmitting && (
          <div className="mx-4 mb-2 flex items-center gap-3 rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-900/10 px-4 py-2.5">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            <p className="flex-1 text-xs text-emerald-700 dark:text-emerald-400">Good picture of symptoms gathered. Ready for clinical review — tap <strong>Submit</strong> below.</p>
            <button onClick={() => setReadyToSubmit(false)} className="text-[10px] text-emerald-600 underline opacity-70">Dismiss</button>
          </div>
        )}

        {/* Submit button — patients only */}
        {user?.role === "patient" && activeConsultation && messages.length > 2 && (
          <div className="border-t border-[hsl(var(--border))] px-4 pt-3 pb-1">
            <button
              id="submit-consultation-btn"
              onClick={handleSubmit}
              disabled={isSubmitting || isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:from-emerald-600 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Running Clinical Pipeline...
                </>
              ) : (
                <>
                  <ClipboardCheck className="h-4 w-4" />
                  Submit for Clinical Review
                </>
              )}
            </button>
            <p className="mt-1.5 text-center text-[10px] text-[hsl(var(--muted-foreground))]">Triggers History, Triage, Medicine, Doctor &amp; Follow-up agents</p>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-[hsl(var(--border))] p-4">
          <div className="flex items-center gap-2 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2 focus-within:ring-2 focus-within:ring-[hsl(var(--ring))]/50">
            <button
              onClick={toggleRecording}
              className={cn(
                "rounded-lg p-2 transition-colors",
                isRecording
                  ? "bg-rose-100 text-rose-600 dark:bg-rose-900/30 animate-pulse"
                  : "hover:bg-[hsl(var(--accent))] text-[hsl(var(--muted-foreground))]"
              )}
              title={isRecording ? "Stop recording" : "Start voice input"}
            >
              {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Describe symptoms, e.g., 'fever for 3 days'..."
              className="flex-1 bg-transparent text-sm outline-none"
            />

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageUpload}
              accept="image/*"
              className="hidden"
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingImage}
              className="rounded-lg p-2 hover:bg-[hsl(var(--accent))] text-[hsl(var(--muted-foreground))] transition-colors"
              title="Attach clinical image"
            >
              {uploadingImage ? <Loader2 className="h-4 w-4 animate-spin" /> : <ImagePlus className="h-4 w-4" />}
            </button>

            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="rounded-xl bg-gradient-primary p-2 text-white transition-all hover:shadow-md disabled:opacity-40"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>

          <p className="mt-2 flex items-center gap-1 text-[10px] text-[hsl(var(--muted-foreground))]">
            <Shield className="h-3 w-3" />
            AI-assisted clinical decision support. All outputs require physician review.
          </p>
        </div>
      </div>

      {/* Sidebar — Agent Progress */}
      <div className="hidden lg:flex w-72 flex-col gap-4">
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-3">Agent Pipeline</h3>
          <div className="space-y-3">
            {[
              { name: "Conversation (Extraction)", key: "conversation" },
              { name: "History (Compilation)", key: "history" },
              { name: "Triage (Priority Classification)", key: "triage" },
              { name: "Medicine (Interaction safety)", key: "medicine" },
              { name: "Doctor (Summary SOAP Note)", key: "doctor" },
              { name: "Follow-up (Care plan schedule)", key: "followup" },
            ].map((agent) => (
              <div key={agent.key} className="flex items-center gap-2.5">
                <div className={cn(
                  "h-2.5 w-2.5 rounded-full transition-all duration-300",
                  pipelineStatus[agent.key] === "active" ? "bg-blue-500 animate-pulse scale-110" :
                  pipelineStatus[agent.key] === "completed" ? "bg-emerald-500" :
                  "bg-slate-200 dark:bg-slate-700"
                )} />
                <span className={cn(
                  "text-xs transition-colors",
                  pipelineStatus[agent.key] === "active" ? "font-semibold text-blue-600 dark:text-blue-400" :
                  pipelineStatus[agent.key] === "completed" ? "font-medium text-emerald-600 dark:text-emerald-400" :
                  "text-[hsl(var(--muted-foreground))]"
                )}>
                  {agent.name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {activeConsultation?.triage_priority && (
          <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 shadow-sm space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[hsl(var(--muted-foreground))]">Triage Output</h4>
            <div className="flex items-center gap-2">
              <span className={cn(
                "rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase",
                activeConsultation.triage_priority === "HIGH" ? "bg-rose-100 text-rose-700 dark:bg-rose-900/20 dark:text-rose-400" :
                activeConsultation.triage_priority === "MEDIUM" ? "bg-amber-100 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400" :
                "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400"
              )}>
                {activeConsultation.triage_priority}
              </span>
            </div>
            <p className="text-[11px] text-[hsl(var(--muted-foreground))] leading-relaxed">{activeConsultation.triage_reasoning}</p>
          </div>
        )}

        <div className="rounded-2xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/10 p-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
            <div>
              <p className="text-xs font-semibold text-amber-700 dark:text-amber-400">Safety Notice</p>
              <p className="mt-1 text-[10px] text-amber-600 dark:text-amber-400/80 leading-relaxed">
                This is a Clinical Decision Support System. AI outputs are advisory only.
                The treating physician makes all medical decisions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
