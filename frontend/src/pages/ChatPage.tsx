import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import ChatPanel from "@/components/chat/ChatPanel";
import * as trainerLinkService from "@/services/trainerLinkService";

/** Chat do ALUNO com um de seus personais (o personal conversa dentro da página do aluno). */
export default function ChatPage() {
  const { linkId = "" } = useParams();
  const { data: links, isLoading } = useQuery({ queryKey: ["my-trainers"], queryFn: trainerLinkService.list });
  const link = links?.find((l) => l.link_id === linkId);

  return (
    <div className="space-y-3">
      <Link to="/perfil" className="text-sm text-accent">‹ Perfil</Link>
      {isLoading && <p className="text-sm text-foreground-muted">Carregando…</p>}
      {!isLoading && !link && <div className="card text-sm text-foreground-muted">Conversa não encontrada ou vínculo encerrado.</div>}
      {link && (
        <>
          <h1 className="text-lg font-semibold">{link.trainer_name}</h1>
          <ChatPanel linkId={link.link_id} otherName={link.trainer_name.split(" ")[0]} />
        </>
      )}
    </div>
  );
}
