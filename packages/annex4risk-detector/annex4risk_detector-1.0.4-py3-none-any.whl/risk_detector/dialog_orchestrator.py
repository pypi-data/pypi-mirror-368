"""Simple dialog orchestrator for CLI demo."""
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .rules_repo import RulesRepo
from .question_builder import build_questions, needed_feature_keys
from .evaluators.jsonlogic_eval import evaluate_rule
from .classifiers.aggregator import classify

class DialogOrchestrator:
    def __init__(self, db_url: str):
        if db_url.startswith("sqlite"):
            self.engine = create_engine(
                db_url, connect_args={"check_same_thread": False}
            )
        else:
            self.engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
        self.Session = sessionmaker(bind=self.engine)

    def start_session(self, customer_id: str = None) -> str:
        with self.Session() as db:
            repo = RulesRepo(db)
            _, _, _, version = repo.load()
            session_id = str(uuid.uuid4())
            chat = models.ChatSession(
                id=session_id, customer_id=customer_id, rule_snapshot_version=version
            )
            db.add(chat)
            db.commit()
            return session_id

    def next_question(self, session_id: str):
        with self.Session() as db:
            chat = db.get(models.ChatSession, session_id)
            if not chat:
                raise RuntimeError(f"Chat session not found: {session_id}")
            repo = RulesRepo(db)
            rules, feats, qs, version = repo.load()
            answers = {a.feature_key: a.value for a in chat.answers}
            questions = build_questions(rules, feats, qs, answers)
            for q in questions:
                if q.feature_key not in answers:
                    return {
                        "feature_key": q.feature_key,
                        "prompt": q.prompt_en or feats[q.feature_key].prompt_en,
                        "type": feats[q.feature_key].type,
                        "options": feats[q.feature_key].options,
                    }
            # ensure required feature coverage before evaluation
            needed = needed_feature_keys(rules)
            needed |= {k for k, f in feats.items() if getattr(f, "required", False)}
            missing = [k for k in needed if k not in answers]
            if missing:
                missing_set = set(missing)
                candidates = [
                    q
                    for q in qs
                    if q.feature_key in missing_set
                    and (not q.gating or evaluate_rule(q.gating, answers))
                ]
                candidates.sort(key=lambda q: getattr(q, "priority", 0))
                if candidates:
                    q = candidates[0]
                    return {
                        "feature_key": q.feature_key,
                        "prompt": q.prompt_en or feats[q.feature_key].prompt_en,
                        "type": feats[q.feature_key].type,
                        "options": feats[q.feature_key].options,
                    }
                raise RuntimeError(f"Missing answers for: {', '.join(missing)}")
            # evaluate
            evaluated = []
            for r in rules:
                cond = evaluate_rule(r.condition, answers)
                evaluated.append(
                    {
                        "id": r.id,
                        "category": r.category,
                        "weight": r.weight,
                        "legal_refs": r.legal_refs,
                        "matched": cond,
                    }
                )
            outcome = classify(evaluated, answers)
            res = models.RiskOutcome(
                id=str(uuid.uuid4()),
                session_id=session_id,
                rule_snapshot_version=version,
                category=outcome["category"],
                score=outcome["score"],
                reasoning=outcome,
                legal_refs=outcome["legal_refs"],
                exception_applied=outcome["exception_applied"],
            )
            db.add(res)
            db.commit()
            return {"outcome": outcome}

    def submit_answer(self, session_id: str, feature_key: str, value):
        with self.Session() as db:
            if not db.get(models.ChatSession, session_id):
                raise RuntimeError(f"Chat session not found: {session_id}")
            ans = models.ChatAnswer(
                id=str(uuid.uuid4()),
                session_id=session_id,
                feature_key=feature_key,
                value=value,
            )
            db.add(ans)
            db.commit()
