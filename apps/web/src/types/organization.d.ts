interface Organizations {
  id: numbers;
  name: string;
  slug: string;
}

interface OrganizationMember {
  id: number | string;
  org_id: number | string;
  user_id: number | string;
  role: string;
}
