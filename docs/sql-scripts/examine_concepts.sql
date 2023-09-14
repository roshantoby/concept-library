-- Examine concept linkage with parent phenotypes
with
  -- det. first appearance of a Concept in a Phenotype
  split_concepts as (
    select phenotype.id as phenotype_id,
           concept->>'concept_id' as concept_id,
           created
      from public.clinicalcode_phenotype as phenotype,
           json_array_elements(phenotype.concept_informations::json) as concept
  ),
  ranked_concepts as (
    select phenotype_id,
           concept_id,
           rank() over (
             partition by concept_id
             order by created
           ) ranking
      from split_concepts
  ),
  -- count distinct appearances
  counts as (
    select
      (select count(distinct id) from public.clinicalcode_concept) as total_concepts,
      (select count(distinct concept_id) from ranked_concepts) as linked_concepts
  )

-- calc. difference
select total_concepts,
       linked_concepts,
       total_concepts - linked_concepts as diff
  from counts;

-- show unlinked concepts
select id, name, author, owner_id, created, modified, group_id
  from public.clinicalcode_concept
 where (is_deleted is null or is_deleted = false)
   and id not in (
     select concept_id::int from ranked_concepts
   );

-------------------------------------------------------------

-- Update concept's ownership
with
    split_concepts as (
      select phenotype.id as phenotype_id, 
          concept ->> 'concept_id' as concept_id,
          created
        from public.clinicalcode_phenotype as phenotype,
          json_array_elements(phenotype.concept_informations :: json) as concept
    ),
    ranked_concepts as (
        select phenotype_id, concept_id,
          rank() over(
            partition by concept_id
                order by created
          ) ranking
          from split_concepts
    )

update public.clinicalcode_concept as trg
    set phenotype_owner_id = src.phenotype_id
   from (
     select distinct on (concept_id) *
       from ranked_concepts
   ) src
  where (trg.is_deleted is null or trg.is_deleted = false)
    and trg.id = src.concept_id::int;

-------------------------------------------------------------

-- Examine concept linkage after initial linking
with
  counts as (
    select
      (
        select count(id)
          from public.clinicalcode_concept
		     where is_deleted is null or is_deleted = false
      ) as total_concepts,
      (
        select count(*)
          from public.clinicalcode_concept
         where phenotype_owner_id is null and (is_deleted is null or is_deleted = false)
      ) as unlinked_concepts
  )

select total_concepts,
	     total_concepts - unlinked_concepts as linked_concepts,
       unlinked_concepts
  from counts;

-------------------------------------------------------------

-- Select unlinked concepts
select id
  from public.clinicalcode_concept
 where (is_deleted is null or is_deleted = false)
   and phenotype_owner_id is null;

-------------------------------------------------------------
