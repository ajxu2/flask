(*
fun allInts ([] : int option list) : bool = true
  | allInts (x::xs) = if x = NONE then false else allInts xs
*)
(* fun allInts (L : int option list) : bool = allInts L *)
fun allInts ([] : int option list) : bool = true
  | allInts (x::xs) = false