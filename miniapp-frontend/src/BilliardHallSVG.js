import React from "react";
import { ReactComponent as BilliardSVG } from "./BilliardHallSVG.svg";

export default function BilliardHallSVG({ className, style }) {
  return (
    <div className={className} style={style}>
      <BilliardSVG style={{ width: "100%", height: "auto", display: "block" }} />
    </div>
  );
}
